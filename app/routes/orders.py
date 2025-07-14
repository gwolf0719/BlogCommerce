import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, date, timedelta

from ..database import get_db
from ..models.order import Order, OrderItem, OrderStatus
from ..models.product import Product
from ..models.user import User
from ..auth import get_current_active_user, get_current_admin_user
from ..services.payment_service import PaymentService
from ..utils.helpers import generate_order_number
from ..schemas.order import OrderResponse, OrderCreate, OrderUpdate

router = APIRouter(prefix="/orders", tags=["訂單"])


# 【核心修正點】: 統一 POST 路由，只保留一個
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """建立新訂單"""
    if not order.items:
        raise HTTPException(status_code=400, detail="訂單必須包含至少一個商品")
    
    subtotal = Decimal("0.00")
    order_items_to_create = []
    
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.is_active == True).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"商品 ID {item.product_id} 不存在或已停用")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"商品 {product.name} 庫存不足，目前庫存：{product.stock_quantity}")
        
        item_total = product.current_price * item.quantity
        subtotal += item_total
        
        order_items_to_create.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_price": product.current_price,
            "quantity": item.quantity
        })
        product.stock_quantity -= item.quantity
    
    discount_amount = Decimal("0.00")
    total_amount = subtotal - discount_amount
    
    db_order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id if current_user else None,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        shipping_address=order.shipping_address,
        subtotal=subtotal,
        discount_amount=discount_amount,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        notes=order.notes,
        payment_method=order.payment_method,
        payment_status=order.payment_status or "pending"
    )
    
    db.add(db_order)
    db.flush()
    
    for item_data in order_items_to_create:
        order_item = OrderItem(order_id=db_order.id, **item_data)
        db.add(order_item)
    
    if order.payment_method:
        try:
            payment_service = PaymentService(db)
            payment_data = payment_service.create_payment_order(
                payment_method=order.payment_method,
                order_id=db_order.order_number,
                amount=total_amount,
                customer_info={'name': order.customer_name, 'email': order.customer_email, 'phone': order.customer_phone}
            )
            if payment_data:
                db_order.payment_info = json.dumps(payment_data)
                db_order.payment_updated_at = datetime.now()
        except Exception as e:
            print(f"自動建立付款訂單失敗: {e}")
    
    db.commit()
    db.refresh(db_order)
    return OrderResponse.from_orm(db_order)


@router.get("/my", response_model=List[OrderResponse])
def get_my_orders(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """獲取目前使用者的所有訂單，並支援狀態和日期篩選"""
    
    query = db.query(Order).filter(Order.user_id == current_user.id)\
              .options(
                  selectinload(Order.items).selectinload(OrderItem.product)
              ).order_by(desc(Order.created_at))

    if status and status != "all":
        try:
            status_enum = OrderStatus[status.lower()]
            query = query.filter(Order.status == status_enum)
        except KeyError:
            pass
    
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    
    if end_date:
        query = query.filter(Order.created_at < (end_date + timedelta(days=1)))

    orders = query.all()
    
    return orders


@router.get("/my/{order_id}", response_model=OrderResponse)
def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取得目前使用者的特定訂單（含商品明細）"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).options(selectinload(Order.items).selectinload(OrderItem.product)).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="訂單不存在或無權限查看")

    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """取得特定訂單（管理員用，含商品明細）"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="訂單不存在")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新訂單狀態（管理員）"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="訂單不存在")

    update_data = order_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db_order.updated_at = datetime.now()
    db.commit()
    db.refresh(db_order)
    return db_order


@router.put("/{order_id}/payment")
def update_order_payment_status(
    order_id: int,
    payment_data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新訂單付款狀態（管理員）"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    # 更新付款相關欄位
    if "payment_method" in payment_data:
        order.payment_method = payment_data["payment_method"]
    
    if "payment_status" in payment_data:
        order.payment_status = payment_data["payment_status"]
    
    if "payment_info" in payment_data:
        order.payment_info = payment_data["payment_info"]
    
    # 更新付款時間
    order.payment_updated_at = datetime.now()
    order.updated_at = datetime.now()
    
    db.commit()
    db.refresh(order)
    
    return {"message": "付款狀態更新成功", "order_id": order_id}
