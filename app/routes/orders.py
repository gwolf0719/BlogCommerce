import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc, func, or_
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, date, timedelta

from ..database import get_db
from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.product import Product
from ..models.user import User
from ..auth import get_current_active_user, get_current_admin_user
from ..services.payment_service import PaymentService
from ..utils.helpers import generate_order_number
from ..schemas.order import (
    OrderResponse, OrderCreate, OrderUpdate, OrderListResponse, 
    OrderStatusUpdate, OrderStatsResponse
)

router = APIRouter(prefix="/orders", tags=["訂單"])


@router.post("/", response_model=OrderResponse, summary="建立新訂單")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """建立新訂單，可由登入使用者或訪客建立。"""
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
    return db_order


@router.get("/stats/overview", response_model=OrderStatsResponse, summary="獲取訂單統計數據 (管理員)")
def get_order_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """提供訂單總數、待處理訂單、今日訂單和總銷售額的統計數據。"""
    total_orders = db.query(func.count(Order.id)).scalar()
    
    processing_orders = db.query(func.count(Order.id)).filter(
        Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED])
    ).scalar()
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_orders = db.query(func.count(Order.id)).filter(Order.created_at >= today_start).scalar()
    
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == PaymentStatus.paid
    ).scalar() or Decimal("0.00")
    
    return OrderStatsResponse(
        total_orders=total_orders,
        processing_orders=processing_orders,
        today_orders=today_orders,
        total_revenue=total_revenue
    )


@router.get("/", response_model=OrderListResponse, summary="獲取訂單列表 (管理員)")
def list_orders(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理員獲取所有訂單，支援分頁、搜尋和篩選。"""
    query = db.query(Order).options(selectinload(Order.items)).order_by(desc(Order.created_at))

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Order.order_number.ilike(search_term),
                Order.customer_name.ilike(search_term),
                Order.customer_email.ilike(search_term)
            )
        )

    if status:
        try:
            status_enum = OrderStatus[status.upper()]
            query = query.filter(Order.status == status_enum)
        except KeyError:
            pass

    if start_date:
        query = query.filter(Order.created_at >= start_date)
    
    if end_date:
        query = query.filter(Order.created_at < (end_date + timedelta(days=1)))

    total = query.count()
    orders = query.offset(skip).limit(limit).all()
    
    return OrderListResponse(items=orders, total=total)


@router.get("/my", response_model=List[OrderResponse], summary="獲取我的訂單")
def get_my_orders(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """獲取目前登入使用者的所有訂單，並支援狀態和日期篩選。"""
    query = db.query(Order).filter(Order.user_id == current_user.id)\
              .options(selectinload(Order.items).selectinload(OrderItem.product))\
              .order_by(desc(Order.created_at))

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


@router.get("/my/{order_id}", response_model=OrderResponse, summary="獲取我的特定訂單")
def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取得目前登入使用者的特定訂單詳情。"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).options(selectinload(Order.items).selectinload(OrderItem.product)).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="訂單不存在或無權限查看")

    return order


@router.get("/{order_id}", response_model=OrderResponse, summary="獲取特定訂單 (管理員)")
def get_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理員取得特定訂單的完整詳情。"""
    order = db.query(Order).options(selectinload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="訂單不存在")
    return order


@router.put("/{order_id}", response_model=OrderResponse, summary="通用更新訂單 (管理員)")
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理員通用更新訂單資訊。"""
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


@router.put("/{order_id}/status", response_model=OrderResponse, summary="更新訂單狀態 (管理員)")
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理員更新訂單的處理狀態 (例如：已出貨、已送達)。"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    order.status = status_update.status
    order.updated_at = datetime.now()
    
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}/payment", response_model=OrderResponse, summary="更新訂單付款狀態 (管理員)")
def update_order_payment_status(
    order_id: int,
    payment_data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """管理員手動更新訂單的付款方式和狀態。"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    if "payment_method" in payment_data:
        order.payment_method = payment_data["payment_method"]
    
    if "payment_status" in payment_data:
        order.payment_status = payment_data["payment_status"]
    
    if "payment_info" in payment_data:
        order.payment_info = payment_data["payment_info"]
    
    order.payment_updated_at = datetime.now()
    order.updated_at = datetime.now()
    
    db.commit()
    db.refresh(order)
    return order


@router.post("/webhook/payment", summary="接收金流 Webhook")
async def payment_webhook(request: Request):
    """接收來自金流服務的 Webhook，自動更新訂單狀態。"""
    data = await request.json()
    
    order_number = data.get("order_number")
    if not order_number:
        raise HTTPException(status_code=400, detail="缺少訂單號")
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.order_number == order_number).first()
        if not order:
            print(f"Webhook 警告：找不到訂單 {order_number}")
            return {"status": "ok"}
        
        payment_service = PaymentService(db)
        success = payment_service.process_webhook(order, data)
        
        if success:
            db.commit()
            return {"status": "ok", "message": f"訂單 {order_number} 狀態已更新"}
        else:
            db.rollback()
            return {"status": "error", "message": "狀態更新失敗"}
    finally:
        db.close()
