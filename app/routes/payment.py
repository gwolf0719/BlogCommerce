"""
金流處理路由
處理各種金流方式的付款流程
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from decimal import Decimal
import json
from datetime import datetime

from ..database import get_db
from ..models.order import Order, PaymentStatus
from ..services.payment_service import PaymentService
from ..auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/payment", tags=["金流處理"])


@router.post("/create")
async def create_payment(
    payment_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """建立付款訂單"""
    try:
        order_id = payment_data.get('order_id')
        payment_method = payment_data.get('payment_method')
        
        # 驗證訂單
        order = db.query(Order).filter(Order.order_number == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="訂單不存在")
        
        # 檢查訂單是否已付款
        if order.payment_status == PaymentStatus.PAID:
            raise HTTPException(status_code=400, detail="訂單已付款")
        
        # 建立付款
        with PaymentService() as payment_service:
            result = payment_service.create_payment_order(
                payment_method=payment_method,
                order_id=order_id,
                amount=order.total_amount,
                customer_info={
                    'name': order.customer_name,
                    'email': order.customer_email,
                    'phone': order.customer_phone
                }
            )
        
        # 更新訂單付款資訊
        order.payment_method = payment_method
        order.payment_status = PaymentStatus.PENDING
        order.payment_info = json.dumps(result)
        order.payment_updated_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": "付款訂單建立成功",
            "data": result
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirm/{payment_method}")
async def confirm_payment(
    payment_method: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """確認付款（回調端點）"""
    try:
        # 取得回調資料
        if request.method == "POST":
            payment_data = await request.json()
        else:
            payment_data = dict(request.query_params)
        
        # 驗證付款
        with PaymentService() as payment_service:
            verification_result = await payment_service.verify_payment(payment_method, payment_data)
        
        if verification_result['success']:
            # 更新訂單狀態
            order_id = payment_data.get('orderId') or payment_data.get('MerchantTradeNo')
            if order_id:
                background_tasks.add_task(update_order_payment_status, order_id, verification_result, db)
            
            return {"success": True, "message": "付款確認成功"}
        else:
            return {"success": False, "message": verification_result.get('message', '付款驗證失敗')}
            
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/status/{order_id}")
async def get_payment_status(
    order_id: str,
    db: Session = Depends(get_db)
):
    """取得付款狀態"""
    order = db.query(Order).filter(Order.order_number == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    return {
        "order_id": order.order_number,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "payment_info": json.loads(order.payment_info) if order.payment_info else None,
        "updated_at": order.payment_updated_at
    }


@router.post("/manual-confirm")
async def manual_confirm_payment(
    confirm_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """手動確認付款（管理員）"""
    try:
        order_id = confirm_data.get('order_id')
        notes = confirm_data.get('notes', '')
        
        # 查找訂單
        order = db.query(Order).filter(Order.order_number == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="訂單不存在")
        
        # 更新付款狀態
        order.payment_status = PaymentStatus.PAID
        order.payment_updated_at = datetime.now()
        
        # 更新付款資訊
        payment_info = json.loads(order.payment_info) if order.payment_info else {}
        payment_info.update({
            'manual_confirmed': True,
            'confirmed_by': current_user.username,
            'confirmed_at': datetime.now().isoformat(),
            'notes': notes
        })
        order.payment_info = json.dumps(payment_info)
        
        db.commit()
        
        return {
            "success": True,
            "message": "付款已手動確認",
            "order_id": order_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refund")
async def refund_payment(
    refund_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """退款處理"""
    try:
        order_id = refund_data.get('order_id')
        refund_amount = refund_data.get('amount')
        reason = refund_data.get('reason', '')
        
        # 查找訂單
        order = db.query(Order).filter(Order.order_number == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="訂單不存在")
        
        if order.payment_status != PaymentStatus.PAID:
            raise HTTPException(status_code=400, detail="訂單未付款，無法退款")
        
        # 處理退款邏輯（這裡簡化為標記狀態）
        order.payment_status = PaymentStatus.REFUNDED
        order.payment_updated_at = datetime.now()
        
        # 更新付款資訊
        payment_info = json.loads(order.payment_info) if order.payment_info else {}
        payment_info.update({
            'refunded': True,
            'refund_amount': str(refund_amount),
            'refund_reason': reason,
            'refunded_by': current_user.username,
            'refunded_at': datetime.now().isoformat()
        })
        order.payment_info = json.dumps(payment_info)
        
        db.commit()
        
        return {
            "success": True,
            "message": "退款處理成功",
            "order_id": order_id,
            "refund_amount": refund_amount
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# 背景任務：更新訂單付款狀態
async def update_order_payment_status(order_id: str, verification_result: Dict, db: Session):
    """更新訂單付款狀態（背景任務）"""
    try:
        order = db.query(Order).filter(Order.order_number == order_id).first()
        if order:
            order.payment_status = PaymentStatus.PAID if verification_result['success'] else PaymentStatus.FAILED
            order.payment_updated_at = datetime.now()
            
            # 更新付款資訊
            payment_info = json.loads(order.payment_info) if order.payment_info else {}
            payment_info.update({
                'verification_result': verification_result,
                'verified_at': datetime.now().isoformat()
            })
            order.payment_info = json.dumps(payment_info)
            
            db.commit()
            
    except Exception as e:
        print(f"更新訂單付款狀態失敗: {e}")
        db.rollback()


# 測試端點
@router.get("/test/{payment_method}")
async def test_payment_method(
    payment_method: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """測試金流設定"""
    try:
        with PaymentService() as payment_service:
            # 建立測試訂單
            test_order_id = f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            test_amount = Decimal('1.00')
            test_customer = {
                'name': '測試客戶',
                'email': 'test@example.com',
                'phone': '0912345678'
            }
            
            result = payment_service.create_payment_order(
                payment_method=payment_method,
                order_id=test_order_id,
                amount=test_amount,
                customer_info=test_customer
            )
            
            return {
                "success": True,
                "message": f"{payment_method} 金流測試成功",
                "test_data": result
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"{payment_method} 金流測試失敗: {str(e)}"
        }