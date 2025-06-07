from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import uuid
from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    CartItem, CartResponse, OrderStatus, OrderItemCreate, OrderItemResponse
)
from app.auth import get_current_active_user, get_current_admin_user
from datetime import datetime

router = APIRouter(prefix="/api/orders", tags=["orders"])


def generate_order_number() -> str:
    """生成訂單編號"""
    import time
    timestamp = str(int(time.time()))
    random_part = str(uuid.uuid4()).split('-')[0].upper()
    return f"ORD{timestamp}{random_part}"


@router.post("/cart/calculate", response_model=CartResponse)
def calculate_cart(cart_items: List[CartItem], db: Session = Depends(get_db)):
    """計算購物車總價"""
    if not cart_items:
        return CartResponse(items=[], total_items=0, total_amount=Decimal("0.00"))
    
    items = []
    total_amount = Decimal("0.00")
    total_items = 0
    
    for cart_item in cart_items:
        product = db.query(Product).filter(
            Product.id == cart_item.product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"商品 ID {cart_item.product_id} 不存在或已停用"
            )
        
        if product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"商品 {product.name} 庫存不足，目前庫存：{product.stock_quantity}"
            )
        
        item_total = product.current_price * cart_item.quantity
        total_amount += item_total
        total_items += cart_item.quantity
        
        items.append({
            "id": 0,  # 購物車項目沒有 ID
            "product_id": product.id,
            "quantity": cart_item.quantity,
            "product_name": product.name,
            "product_price": product.current_price,
            "total_price": item_total,
            "created_at": "",
            "updated_at": None
        })
    
    return CartResponse(
        items=items,
        total_items=total_items,
        total_amount=total_amount
    )


@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """建立新訂單"""
    if not order.items:
        raise HTTPException(status_code=400, detail="訂單必須包含至少一個商品")
    
    # 計算訂單總價並檢查庫存
    subtotal = Decimal("0.00")
    order_items = []
    
    for item in order.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"商品 ID {item.product_id} 不存在或已停用"
            )
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"商品 {product.name} 庫存不足，目前庫存：{product.stock_quantity}"
            )
        
        item_total = product.current_price * item.quantity
        subtotal += item_total
        
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_price": product.current_price,
            "quantity": item.quantity
        })
        
        # 扣除庫存
        product.stock_quantity -= item.quantity
    
    # 計算運費（這裡可以根據業務規則調整）
    shipping_fee = Decimal("60.00") if subtotal < Decimal("1000.00") else Decimal("0.00")
    total_amount = subtotal + shipping_fee
    
    # 建立訂單
    db_order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id if current_user else None,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        shipping_address=order.shipping_address,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total_amount=total_amount,
        status=OrderStatus.PENDING,

        notes=order.notes
    )
    
    db.add(db_order)
    db.flush()  # 取得訂單 ID
    
    # 建立訂單項目
    for item_data in order_items:
        order_item = OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/", response_model=List[OrderListResponse])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status: Optional[OrderStatus] = None,
    db: Session = Depends(get_db)
):
    """取得所有訂單 (管理員用)"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/my", response_model=List[OrderResponse])
def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取得目前使用者的訂單"""
    query = db.query(Order).filter(Order.customer_email == current_user.email)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/my/{order_id}", response_model=OrderResponse)
def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取得目前使用者的特定訂單"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_email == current_user.email
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在或無權限查看"
        )
    
    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """取得特定訂單 (管理員用)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    return order


@router.get("/number/{order_number}", response_model=OrderResponse)
def get_order_by_number(
    order_number: str,
    customer_email: str,
    db: Session = Depends(get_db)
):
    """透過訂單編號和電子郵件查詢訂單（訪客查詢）"""
    order = db.query(Order).filter(
        Order.order_number == order_number,
        Order.customer_email == customer_email
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在或電子郵件不符")
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """更新訂單 (管理員用)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    
    return order


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """刪除訂單 (管理員用)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    db.delete(order)
    db.commit()
    
    return {"message": "訂單已刪除"}


@router.get("/stats/overview")
def get_order_stats(db: Session = Depends(get_db)):
    """取得訂單統計 (管理員用)"""
    from sqlalchemy import func
    
    # 總訂單數
    total_orders = db.query(func.count(Order.id)).scalar()
    
    # 各狀態訂單數
    pending_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.pending).scalar()
    processing_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.processing).scalar()
    shipped_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.shipped).scalar()
    delivered_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.delivered).scalar()
    cancelled_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.cancelled).scalar()
    
    # 總營收
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_([OrderStatus.delivered, OrderStatus.shipped])
    ).scalar() or 0
    
    # 平均訂單金額
    avg_order_amount = db.query(func.avg(Order.total_amount)).scalar() or 0
    
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "processing_orders": processing_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
        "total_revenue": float(total_revenue),
        "avg_order_amount": float(avg_order_amount)
    } 