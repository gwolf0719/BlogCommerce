"""
金流處理服務
支援轉帳、Line Pay、綠界、PayPal 等金流方式
"""

import json
import hashlib
import hmac
import base64
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
import urllib.parse

import httpx
import paypalrestsdk
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ..models.settings import SystemSettings
from ..database import SessionLocal
from ..models.order import Order, PaymentStatus, PaymentMethod


class PaymentService:
    """金流處理服務"""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = self._load_payment_settings()
    
    def _load_payment_settings(self) -> Dict[str, Any]:
        """【已修正】載入金流設定"""
        settings = {}
        # 使用後台儲存的詳細設定鍵名
        payment_keys = [
            'payment_transfer_details',
            'payment_linepay_details',
            'payment_ecpay_details',
            'payment_paypal_details'
        ]
        
        for key in payment_keys:
            setting = self.db.query(SystemSettings).filter(SystemSettings.key == key).first()
            if setting and setting.value:
                try:
                    # 將 _details 去掉，方便後續程式碼以 payment_transfer 的方式取用
                    simple_key = key.replace('_details', '')
                    settings[simple_key] = json.loads(setting.value) if setting.data_type == 'json' else setting.value
                except (json.JSONDecodeError, TypeError):
                    settings[key.replace('_details', '')] = None
        
        return settings
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 在服務結束時不應該關閉 db session，讓 FastAPI 的依賴注入系統管理
        pass
    
    # --- 通用方法 ---
    def create_payment_order(self, payment_method: str, order_id: str, amount: Decimal, customer_info: Dict) -> Optional[Dict[str, Any]]:
        """
        【核心修正點 1】: 修正參數傳遞邏輯
        建立付款訂單（通用入口）
        - 根據 order_id 查詢完整的 Order 物件，再傳遞給對應的處理函式。
        """
        order = self.db.query(Order).filter(Order.order_number == order_id).first()
        if not order:
            raise ValueError(f"訂單 {order_id} 不存在")

        if payment_method == 'transfer':
            return self.create_transfer_order(order)
        elif payment_method == 'linepay':
            return self.create_linepay_payment(order)
        elif payment_method == 'ecpay':
            return self.create_ecpay_payment(order)
        elif payment_method == 'paypal':
            return self.create_paypal_order(order)
        else:
            raise ValueError(f"不支援的付款方式: {payment_method}")
            
    # --- 轉帳相關方法 ---
    def create_transfer_order(self, order: Order) -> Dict[str, Any]:
        """
        【核心修正點 2】: 修正回傳資料結構
        建立轉帳訂單，回傳前端需要的扁平化 JSON 結構。
        """
        transfer_config = self.settings.get('payment_transfer')
        if not transfer_config or not all(k in transfer_config for k in ['bank', 'account', 'name']):
            raise ValueError("轉帳設定未設置或不完整")
        
        return {
            'payment_method': 'transfer',
            'order_id': order.order_number,
            'amount': str(order.total_amount),
            'bank_name': transfer_config.get('bank'),
            'account_name': transfer_config.get('name'),
            'account_number': transfer_config.get('account'),
            'note': "請在3天內完成轉帳，並在備註中填寫您的訂單號碼以便核對。"
        }
    
    # --- Line Pay 相關方法 ---
    def create_linepay_payment(self, order: Order) -> Dict[str, Any]:
        """建立 Line Pay 付款請求"""
        settings = self.settings.get("payment_linepay")
        if not settings:
            raise Exception("Line Pay 設定未完成")
        
        request_data = {
            "amount": int(order.total_amount),
            "currency": "TWD",
            "orderId": order.order_number,
            "packages": [{
                "id": order.order_number,
                "amount": int(order.total_amount),
                "products": [
                    {
                        "name": item.product_name,
                        "quantity": item.quantity,
                        "price": int(item.product_price)
                    }
                    for item in order.items
                ]
            }],
            "redirectUrls": {
                "confirmUrl": f"http://localhost:8001/api/payment/linepay/confirm",
                "cancelUrl": f"http://localhost:8001/api/payment/linepay/cancel"
            }
        }
        
        nonce = str(int(datetime.now().timestamp() * 1000))
        uri = "/v3/payments/request"
        message = settings["channel_secret"] + uri + json.dumps(request_data, separators=(',', ':')) + nonce
        signature = base64.b64encode(
            hmac.new(
                settings["channel_secret"].encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": settings["channel_id"],
            "X-LINE-Authorization-Nonce": nonce,
            "X-LINE-Authorization": signature
        }
        
        response = requests.post(
            "https://sandbox-api-pay.line.me/v3/payments/request",
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("returnCode") == "0000":
                order.payment_method = PaymentMethod.linepay
                order.payment_status = PaymentStatus.pending
                order.payment_info = json.dumps({
                    "transaction_id": result["info"]["transactionId"],
                    "payment_url": result["info"]["paymentUrl"]["web"],
                    "created_at": datetime.now().isoformat()
                })
                self.db.commit()
                return {
                    "success": True,
                    "payment_url": result["info"]["paymentUrl"]["web"],
                    "transaction_id": result["info"]["transactionId"]
                }
            else:
                raise Exception(f"Line Pay 請求失敗: {result.get('returnMessage', '未知錯誤')}")
        else:
            raise Exception(f"Line Pay API 請求失敗: HTTP {response.status_code}")
    
    # --- 綠界相關方法 ---
    def create_ecpay_payment(self, order: Order) -> Dict[str, Any]:
        """建立綠界付款請求"""
        settings = self.settings.get("payment_ecpay")
        if not settings:
            raise Exception("綠界設定未完成")
        
        request_data = {
            "MerchantID": settings["merchant_id"],
            "MerchantTradeNo": order.order_number,
            "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "PaymentType": "aio",
            "TotalAmount": int(order.total_amount),
            "TradeDesc": f"訂單 {order.order_number}",
            "ItemName": "#".join([f"{item.product_name} x{item.quantity}" for item in order.items]),
            "ReturnURL": f"http://localhost:8001/api/payment/ecpay/callback",
            "ChoosePayment": "ALL",
            "EncryptType": "1"
        }
        
        check_value = self._create_ecpay_check_value(request_data, settings["hash_key"], settings["hash_iv"])
        request_data["CheckMacValue"] = check_value
        
        order.payment_method = PaymentMethod.ecpay
        order.payment_status = PaymentStatus.pending
        order.payment_info = json.dumps({
            "merchant_trade_no": order.order_number,
            "created_at": datetime.now().isoformat()
        })
        self.db.commit()
        
        return {
            "success": True,
            "form_data": request_data,
            "action_url": settings.get("api_url", "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5")
        }
    
    def _create_ecpay_check_value(self, data: Dict, hash_key: str, hash_iv: str) -> str:
        """建立綠界檢查碼"""
        sorted_data = sorted(data.items())
        raw_string = "&".join([f"{k}={v}" for k, v in sorted_data])
        raw_string = f"HashKey={hash_key}&{raw_string}&HashIV={hash_iv}"
        encoded_string = urllib.parse.quote_plus(raw_string).lower()
        return hashlib.sha256(encoded_string.encode('utf-8')).hexdigest().upper()
    
    # --- PayPal 相關方法 ---
    def create_paypal_order(self, order: Order) -> Dict[str, Any]:
        """建立 PayPal 訂單"""
        paypal_config = self.settings.get('payment_paypal')
        if not paypal_config:
            raise ValueError("PayPal 設定未設置")
        
        paypalrestsdk.configure({
            "mode": paypal_config.get('environment', 'sandbox'),
            "client_id": paypal_config.get('client_id'),
            "client_secret": paypal_config.get('client_secret')
        })
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"http://localhost:8002/payment/paypal/return?orderId={order.order_number}",
                "cancel_url": f"http://localhost:8002/payment/paypal/cancel?orderId={order.order_number}"
            },
            "transactions": [{
                "item_list": {
                    "items": [{"name": item.product_name, "sku": str(item.product_id), "price": str(item.product_price), "currency": "TWD", "quantity": item.quantity} for item in order.items]
                },
                "amount": {"total": str(order.total_amount), "currency": "TWD"},
                "description": f"訂單 {order.order_number} 付款"
            }]
        })
        
        if payment.create():
            approval_url = next((link.href for link in payment.links if link.rel == "approval_url"), None)
            if approval_url:
                order.payment_method = PaymentMethod.paypal
                order.payment_status = PaymentStatus.pending
                order.payment_info = json.dumps({"payment_id": payment.id})
                self.db.commit()
                return {'success': True, 'payment_url': approval_url}
        
        raise ValueError(f"PayPal 建立訂單失敗: {payment.error}")
    
    # --- 付款驗證與回呼處理 ---
    async def verify_payment(self, payment_method: str, payment_data: Dict) -> Dict[str, Any]:
        """驗證付款結果"""
        if payment_method == 'linepay':
            return await self._verify_linepay_payment(payment_data)
        elif payment_method == 'ecpay':
            return self._verify_ecpay_payment(payment_data)
        elif payment_method == 'paypal':
            return self._verify_paypal_payment(payment_data)
        else:
            return {'success': False, 'message': f'不支援的付款方式: {payment_method}'}
    
    async def _verify_linepay_payment(self, payment_data: Dict) -> Dict[str, Any]:
        """驗證 Line Pay 付款"""
        linepay_config = self.settings.get('payment_linepay')
        transaction_id = payment_data.get('transactionId')
        api_url = f"https://sandbox-api-pay.line.me/v3/payments/{transaction_id}/confirm"
        headers = {
            'Content-Type': 'application/json',
            'X-LINE-ChannelId': linepay_config.get('channel_id'),
            'X-LINE-ChannelSecret': linepay_config.get('channel_secret')
        }
        payload = {'amount': payment_data.get('amount'), 'currency': 'TWD'}
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=payload)
            result = response.json()
            return {'success': result.get('returnCode') == '0000', 'message': result.get('returnMessage'), 'data': result}
    
    def _verify_ecpay_payment(self, payment_data: Dict) -> Dict[str, Any]:
        """驗證綠界付款"""
        ecpay_config = self.settings.get('payment_ecpay')
        received_mac = payment_data.pop('CheckMacValue', '')
        calculated_mac = self._create_ecpay_check_value(payment_data, ecpay_config["hash_key"], ecpay_config["hash_iv"])
        success = received_mac == calculated_mac and payment_data.get('RtnCode') == '1'
        return {'success': success, 'message': payment_data.get('RtnMsg', ''), 'data': payment_data}
    
    def _verify_paypal_payment(self, payment_data: Dict) -> Dict[str, Any]:
        """驗證 PayPal 付款"""
        paypal_config = self.settings.get('payment_paypal')
        paypalrestsdk.configure({
            "mode": paypal_config.get('environment', 'sandbox'),
            "client_id": paypal_config.get('client_id'),
            "client_secret": paypal_config.get('client_secret')
        })
        payment = paypalrestsdk.Payment.find(payment_data.get('paymentId'))
        if payment.execute({"payer_id": payment_data.get('PayerID')}):
            return {'success': True, 'message': '付款成功', 'data': payment.to_dict()}
        else:
            return {'success': False, 'message': f'付款失敗: {payment.error}', 'data': payment.error}

    def get_payment_settings(self, method: str) -> Optional[Dict]:
        """取得特定金流設定"""
        # 修正鍵名以匹配 _load_payment_settings 的邏輯
        key = f"payment_{method}_details"
        setting = self.db.query(SystemSettings).filter(SystemSettings.key == key).first()
        
        if setting and setting.value:
            try:
                return json.loads(setting.value)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    def handle_linepay_callback(self, transaction_id: str, order_id: str) -> Dict[str, Any]:
        """處理 Line Pay 回傳"""
        order = self.db.query(Order).filter(Order.order_number == order_id).first()
        if not order:
            raise Exception("訂單不存在")
        
        settings = self.settings.get("payment_linepay")
        if not settings:
            raise Exception("Line Pay 設定未完成")
        
        confirm_data = {
            "amount": int(order.total_amount),
            "currency": "TWD"
        }
        
        nonce = str(int(datetime.now().timestamp() * 1000))
        uri = f"/v3/payments/{transaction_id}/confirm"
        message = settings["channel_secret"] + uri + json.dumps(confirm_data, separators=(',', ':')) + nonce
        signature = base64.b64encode(
            hmac.new(
                settings["channel_secret"].encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": settings["channel_id"],
            "X-LINE-Authorization-Nonce": nonce,
            "X-LINE-Authorization": signature
        }
        
        response = requests.post(
            f"https://sandbox-api-pay.line.me/v3/payments/{transaction_id}/confirm",
            headers=headers,
            json=confirm_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("returnCode") == "0000":
                order.payment_status = PaymentStatus.paid
                current_info = json.loads(order.payment_info or '{}')
                current_info.update({
                    "confirmed_at": datetime.now().isoformat(),
                    "line_pay_info": result["info"]
                })
                order.payment_info = json.dumps(current_info)
                order.payment_updated_at = datetime.now()
                self.db.commit()
                return {"success": True, "message": "付款成功"}
            else:
                order.payment_status = PaymentStatus.failed
                current_info = json.loads(order.payment_info or '{}')
                current_info.update({
                    "failed_at": datetime.now().isoformat(),
                    "error_message": result.get("returnMessage", "付款失敗")
                })
                order.payment_info = json.dumps(current_info)
                order.payment_updated_at = datetime.now()
                self.db.commit()
                return {"success": False, "message": result.get("returnMessage", "付款失敗")}
        else:
            raise Exception(f"Line Pay 確認 API 請求失敗: HTTP {response.status_code}")
    
    def handle_ecpay_callback(self, callback_data: Dict) -> Dict[str, Any]:
        """處理綠界回傳"""
        merchant_trade_no = callback_data.get("MerchantTradeNo")
        if not merchant_trade_no:
            raise Exception("缺少訂單編號")
        
        order = self.db.query(Order).filter(Order.order_number == merchant_trade_no).first()
        if not order:
            raise Exception("訂單不存在")
        
        settings = self.settings.get("payment_ecpay")
        if not settings:
            raise Exception("綠界設定未完成")
        
        check_data = {k: v for k, v in callback_data.items() if k != "CheckMacValue"}
        expected_check = self._create_ecpay_check_value(check_data, settings["hash_key"], settings["hash_iv"])
        
        if callback_data.get("CheckMacValue") != expected_check:
            raise Exception("檢查碼驗證失敗")
        
        rtn_code = callback_data.get("RtnCode")
        current_info = json.loads(order.payment_info or '{}')
        
        if rtn_code == "1":
            order.payment_status = PaymentStatus.paid
            current_info.update({
                "paid_at": datetime.now().isoformat(),
                "ecpay_info": callback_data
            })
        else:
            order.payment_status = PaymentStatus.failed
            current_info.update({
                "failed_at": datetime.now().isoformat(),
                "error_message": callback_data.get("RtnMsg", "付款失敗"),
                "ecpay_info": callback_data
            })
        
        order.payment_info = json.dumps(current_info)
        order.payment_updated_at = datetime.now()
        self.db.commit()
        
        return {"success": rtn_code == "1", "message": callback_data.get("RtnMsg", "")}
