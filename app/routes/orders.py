from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import uuid
from app.database import get_db
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    CartItem, CartResponse, OrderItemCreate, OrderItemResponse
)
from app.services.payment_service import PaymentService
from app.auth import get_current_active_user, get_current_admin_user
from datetime import datetime
from sqlalchemy import func, and_
from pydantic import BaseModel

router = APIRouter(prefix="/api/orders", tags=["訂單"])


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


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
    
    # 計算折扣金額（暫時設為 0，未來可以添加其他折扣機制）
    discount_amount = Decimal("0.00")
    
    # 計算最終總金額
    total_amount = subtotal - discount_amount
    
    # 建立訂單
    db_order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id if current_user else None,  # type: ignore
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        shipping_address=order.shipping_address,
        subtotal=subtotal,
        discount_amount=discount_amount,
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
    
    # 記錄折扣使用（未來可以擴展其他折扣機制）
    # 目前暫時移除優惠券功能
    
    # 如果指定了付款方式，自動建立付款訂單
    payment_data = None
    if order.payment_method:
        try:
            with PaymentService() as payment_service:
                payment_data = payment_service.create_payment_order(
                    payment_method=order.payment_method,
                    order_id=db_order.order_number,
                    amount=total_amount,
                    customer_info={
                        'name': order.customer_name,
                        'email': order.customer_email,
                        'phone': order.customer_phone
                    }
                )
                
                # 更新訂單付款資訊
                db_order.payment_method = order.payment_method
                db_order.payment_status = order.payment_status or "pending"
                import json
                db_order.payment_info = json.dumps(payment_data) if payment_data else None
                db_order.payment_updated_at = datetime.now()
                
        except Exception as e:
            # 如果自動建立付款失敗，不影響訂單建立，但記錄錯誤
            print(f"自動建立付款訂單失敗: {e}")
    
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
    from sqlalchemy.orm import selectinload
    
    query = db.query(Order).options(selectinload(Order.items))
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    
    # 轉換為 OrderListResponse 格式
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items_count": len(order.items)
        })
    
    return result


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
async def get_order_stats_overview(
    db: Session = Depends(get_db)
):
    """獲取訂單總體統計"""
    try:
        # 計算總訂單數
        total_orders = db.query(func.count(Order.id)).scalar()
        
        # 計算各狀態訂單數
        pending_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PENDING).scalar()
        confirmed_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.CONFIRMED).scalar()
        shipped_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.SHIPPED).scalar()
        delivered_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.DELIVERED).scalar()
        cancelled_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.CANCELLED).scalar()
        
        # 計算總銷售額
        total_revenue = db.query(
            func.coalesce(func.sum(Order.total_amount), 0)
        ).filter(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED])).scalar()
        
        # 計算今日訂單數
        today = datetime.now().date()
        today_orders = db.query(func.count(Order.id)).filter(
            func.date(Order.created_at) == today
        ).scalar()
        
        # 計算今日銷售額
        today_revenue = db.query(
            func.coalesce(func.sum(Order.total_amount), 0)
        ).filter(
            and_(
                func.date(Order.created_at) == today,
                Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
            )
        ).scalar()
        
        return {
            "total_orders": total_orders or 0,
            "pending_orders": pending_orders or 0,
            "confirmed_orders": confirmed_orders or 0,
            "shipped_orders": shipped_orders or 0,
            "delivered_orders": delivered_orders or 0,
            "cancelled_orders": cancelled_orders or 0,
            "completed_orders": delivered_orders or 0,
            "processing_orders": (pending_orders or 0) + (confirmed_orders or 0) + (shipped_orders or 0),
            "total_revenue": float(total_revenue or 0),
            "today_orders": today_orders or 0,
            "today_revenue": float(today_revenue or 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取訂單統計失敗: {str(e)}")


# 添加路由別名以符合前端API調用
@router.get("/stats")
async def get_order_stats_alias(
    db: Session = Depends(get_db)
):
    """獲取訂單統計（別名路由）"""
    return await get_order_stats_overview(db)


@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新訂單狀態 (管理員用)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="訂單不存在"
        )
    
    # 檢查狀態轉換是否合理
    if order.status == OrderStatus.CANCELLED and status_update.status != OrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已取消的訂單無法變更狀態"
        )
    
    if order.status == OrderStatus.DELIVERED and status_update.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已送達的訂單只能設為取消"
        )
    
    order.status = status_update.status
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return {"message": f"訂單狀態已更新為 {status_update.status.value}", "order": order}


@router.put("/{order_id}/payment")
async def update_order_payment_status(
    order_id: int,
    payment_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """更新訂單付款狀態（僅管理員）"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    # 更新付款相關欄位
    if "payment_method" in payment_data:
        if payment_data["payment_method"]:
            order.payment_method = PaymentMethod(payment_data["payment_method"])
        else:
            order.payment_method = None
    
    if "payment_status" in payment_data:
        if payment_data["payment_status"]:
            order.payment_status = PaymentStatus(payment_data["payment_status"])
        else:
            order.payment_status = PaymentStatus.UNPAID
    
    if "payment_info" in payment_data:
        order.payment_info = payment_data["payment_info"]
    
    if "payment_updated_at" in payment_data:
        from datetime import datetime
        order.payment_updated_at = datetime.fromisoformat(payment_data["payment_updated_at"].replace('Z', '+00:00'))
    
    try:
        db.commit()
        db.refresh(order)
        
        return {
            "id": order.id,
            "payment_method": order.payment_method.value if order.payment_method else None,
            "payment_status": order.payment_status.value if order.payment_status else None,
            "payment_info": order.payment_info,
            "payment_updated_at": order.payment_updated_at.isoformat() if order.payment_updated_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新付款狀態失敗: {str(e)}")


@router.post("/test")
def test_post_endpoint():
    """測試POST端點"""
    return {"message": "POST test endpoint works"}


@router.post("/simple")
def create_order_simple(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """簡化版訂單創建端點"""
    try:
        # 簡單驗證
        if not order.items:
            raise HTTPException(status_code=400, detail="訂單必須包含至少一個商品")
        
        # 創建基本訂單
        db_order = Order(
            order_number=generate_order_number(),
            user_id=current_user.id if current_user else None,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            customer_phone=order.customer_phone,
            shipping_address=order.shipping_address,
            subtotal=Decimal("1000.00"),  # 簡化為固定值
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            status=OrderStatus.PENDING,
            notes=order.notes
        )
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        return {"message": "訂單創建成功", "order_id": db_order.id, "order_number": db_order.order_number}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"創建訂單失敗: {str(e)}") 