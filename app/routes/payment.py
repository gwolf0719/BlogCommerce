"""
金流處理路由
處理各種金流方式的付款流程
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from decimal import Decimal
import json
from datetime import datetime

from ..database import get_db
from ..models.order import Order, PaymentStatus
from ..services.payment_service import PaymentService
from ..auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/payment", tags=["金流處理"])


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
        if order.payment_status == PaymentStatus.paid:
            raise HTTPException(status_code=400, detail="訂單已付款")
        
        # 建立付款
        payment_service = PaymentService(db)
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
        order.payment_status = PaymentStatus.pending
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
        order.payment_status = PaymentStatus.paid
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
        
        if order.payment_status != PaymentStatus.paid:
            raise HTTPException(status_code=400, detail="訂單未付款，無法退款")
        
        # 處理退款邏輯（這裡簡化為標記狀態）
        order.payment_status = PaymentStatus.refunded
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
            order.payment_status = PaymentStatus.paid if verification_result['success'] else PaymentStatus.failed
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


@router.get("/test/{payment_method}")
async def test_payment_method(
    payment_method: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """測試金流方法設定"""
    try:
        # 建立測試訂單資料
        test_order_data = {
            "order_id": f"TEST_{int(datetime.now().timestamp())}",
            "amount": Decimal("100.00"),
            "customer_info": {
                "name": "測試用戶",
                "email": "test@example.com",
                "phone": "0912345678"
            }
        }
        
        with PaymentService() as payment_service:
            result = payment_service.create_payment_order(
                payment_method=payment_method,
                **test_order_data
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


@router.post("/linepay/create/{order_id}")
async def create_linepay_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """建立 Line Pay 付款"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    # 檢查訂單是否屬於當前用戶
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="無權限存取此訂單")
    
    try:
        payment_service = PaymentService(db)
        result = payment_service.create_linepay_payment(order)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/linepay/confirm")
async def linepay_confirm(
    request: Request,
    transactionId: str,
    orderId: str,
    db: Session = Depends(get_db)
):
    """Line Pay 確認回調"""
    try:
        payment_service = PaymentService(db)
        result = payment_service.handle_linepay_callback(transactionId, orderId)
        
        if result["success"]:
            return RedirectResponse(url=f"/payment/success?orderId={orderId}")
        else:
            return RedirectResponse(url=f"/payment/failed?orderId={orderId}&error={result['message']}")
    except Exception as e:
        return RedirectResponse(url=f"/payment/failed?orderId={orderId}&error={str(e)}")


@router.get("/linepay/cancel")
async def linepay_cancel(
    orderId: str,
    db: Session = Depends(get_db)
):
    """Line Pay 取消回調"""
    return RedirectResponse(url=f"/payment/cancelled?orderId={orderId}")


@router.post("/ecpay/create/{order_id}")
async def create_ecpay_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """建立綠界付款"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    # 檢查訂單是否屬於當前用戶
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="無權限存取此訂單")
    
    try:
        payment_service = PaymentService(db)
        result = payment_service.create_ecpay_payment(order)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ecpay/callback")
async def ecpay_callback(
    request: Request,
    db: Session = Depends(get_db),
    MerchantID: str = Form(...),
    MerchantTradeNo: str = Form(...),
    RtnCode: str = Form(...),
    RtnMsg: str = Form(...),
    TradeNo: str = Form(None),
    TradeAmt: str = Form(None),
    PaymentDate: str = Form(None),
    PaymentType: str = Form(None),
    PaymentTypeChargeFee: str = Form(None),
    TradeDate: str = Form(None),
    SimulatePaid: str = Form(None),
    CheckMacValue: str = Form(...)
):
    """綠界付款回調"""
    try:
        callback_data = {
            "MerchantID": MerchantID,
            "MerchantTradeNo": MerchantTradeNo,
            "RtnCode": RtnCode,
            "RtnMsg": RtnMsg,
            "TradeNo": TradeNo,
            "TradeAmt": TradeAmt,
            "PaymentDate": PaymentDate,
            "PaymentType": PaymentType,
            "PaymentTypeChargeFee": PaymentTypeChargeFee,
            "TradeDate": TradeDate,
            "SimulatePaid": SimulatePaid,
            "CheckMacValue": CheckMacValue
        }
        
        payment_service = PaymentService(db)
        result = payment_service.handle_ecpay_callback(callback_data)
        
        return "1|OK" if result["success"] else "0|Fail"
    except Exception as e:
        return f"0|Error: {str(e)}"


@router.get("/transfer/info/{order_id}")
async def get_transfer_info(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """取得銀行轉帳資訊"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    # 檢查訂單是否屬於當前用戶
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="無權限存取此訂單")
    
    try:
        payment_service = PaymentService(db)
        result = payment_service.create_transfer_order(order)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 付款完成頁面
@router.get("/success", response_class=HTMLResponse)
async def payment_success(orderId: str):
    """付款成功頁面"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>付款成功</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .success {{ color: green; font-size: 24px; margin-bottom: 20px; }}
            .order-id {{ font-size: 18px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="success">✅ 付款成功！</div>
        <div class="order-id">訂單編號：{orderId}</div>
        <p>感謝您的購買，我們將盡快為您處理訂單。</p>
        <a href="/">返回首頁</a>
    </body>
    </html>
    """


@router.get("/failed", response_class=HTMLResponse)
async def payment_failed(orderId: str, error: str = "付款失敗"):
    """付款失敗頁面"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>付款失敗</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .failed {{ color: red; font-size: 24px; margin-bottom: 20px; }}
            .order-id {{ font-size: 18px; color: #666; }}
            .error {{ color: #cc0000; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="failed">❌ 付款失敗</div>
        <div class="order-id">訂單編號：{orderId}</div>
        <div class="error">錯誤原因：{error}</div>
        <p>請稍後再試或聯繫客服。</p>
        <a href="/">返回首頁</a>
    </body>
    </html>
    """


@router.get("/cancelled", response_class=HTMLResponse)
async def payment_cancelled(orderId: str):
    """付款取消頁面"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>付款取消</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .cancelled {{ color: orange; font-size: 24px; margin-bottom: 20px; }}
            .order-id {{ font-size: 18px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="cancelled">⚠️ 付款已取消</div>
        <div class="order-id">訂單編號：{orderId}</div>
        <p>您已取消付款，如需繼續購買請重新下單。</p>
        <a href="/">返回首頁</a>
    </body>
    </html>
    """