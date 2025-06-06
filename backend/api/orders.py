from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from database import get_db, settings
from models.models import Order, OrderItem, Product, User
from models.schemas import (
    Order as OrderSchema, OrderCreate, OrderUpdate, OrderSummary,
    OrderItem as OrderItemSchema
)
from api.auth import get_current_admin_user, get_current_user
from utils.helpers import generate_order_number, calculate_shipping_cost

router = APIRouter()

@router.get("/", response_model=List[OrderSummary])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """取得訂單列表 (管理員)"""
    query = db.query(Order)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """取得單一訂單"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    return order

@router.get("/number/{order_number}", response_model=OrderSchema)
async def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """透過訂單編號取得訂單"""
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    return order

@router.post("/", response_model=OrderSchema)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """建立新訂單"""
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="訂單必須包含至少一個商品"
        )
    
    # 驗證商品和計算總金額
    total_amount = 0
    order_items_data = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 ID {item.product_id} 不存在"
            )
        
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 {product.name} 已下架"
            )
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 {product.name} 庫存不足，剩餘 {product.stock_quantity} 件"
            )
        
        # 使用目前價格或特價
        unit_price = product.sale_price if product.sale_price else product.price
        total_price = unit_price * item.quantity
        total_amount += total_price
        
        order_items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "total_price": total_price
        })
    
    # 計算運費
    shipping_cost = calculate_shipping_cost(
        total_amount,
        settings.free_shipping_threshold,
        settings.shipping_cost
    )
    
    # 建立訂單
    order_number = generate_order_number()
    db_order = Order(
        order_number=order_number,
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        customer_phone=order_data.customer_phone,
        shipping_address=order_data.shipping_address,
        shipping_method=order_data.shipping_method,
        shipping_cost=shipping_cost,
        payment_method=order_data.payment_method,
        total_amount=total_amount + shipping_cost
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # 建立訂單項目並更新庫存
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(order_item)
        
        # 減少商品庫存
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        product.stock_quantity -= item_data["quantity"]
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新訂單狀態 (管理員)"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    update_data = order_data.dict(exclude_unset=True)
    
    # 如果取消訂單，需要恢復庫存
    if update_data.get("status") == "cancelled" and db_order.status != "cancelled":
        for item in db_order.order_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity
    
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/status/summary")
async def get_order_status_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """取得訂單狀態統計"""
    from sqlalchemy import func
    
    result = db.query(
        Order.status,
        func.count(Order.id).label('count'),
        func.sum(Order.total_amount).label('total_amount')
    ).group_by(Order.status).all()
    
    summary = {}
    for status, count, total_amount in result:
        summary[status] = {
            "count": count,
            "total_amount": total_amount or 0
        }
    
    return summary

@router.get("/my-orders/", response_model=List[OrderSummary])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取得使用者的訂單列表"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    return orders 