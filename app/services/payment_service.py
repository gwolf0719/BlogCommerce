"""
金流處理服務
支援轉帳、Line Pay、綠界、PayPal 等金流方式
"""

import json
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal

import httpx
import paypalrestsdk
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ..models.settings import SystemSettings
from ..database import SessionLocal


class PaymentService:
    """金流處理服務"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.settings = self._load_payment_settings()
    
    def _load_payment_settings(self) -> Dict[str, Any]:
        """載入金流設定"""
        settings = {}
        payment_keys = ['payment_transfer', 'payment_linepay', 'payment_ecpay', 'payment_paypal']
        
        for key in payment_keys:
            setting = self.db.query(SystemSettings).filter(SystemSettings.key == key).first()
            if setting and setting.value:
                try:
                    settings[key] = json.loads(setting.value) if setting.data_type == 'json' else setting.value
                except:
                    settings[key] = None
        
        return settings
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    # 轉帳相關方法
    def create_transfer_order(self, order_id: str, amount: Decimal, customer_info: Dict) -> Dict[str, Any]:
        """建立轉帳訂單"""
        transfer_config = self.settings.get('payment_transfer')
        if not transfer_config:
            raise ValueError("轉帳設定未設置")
        
        return {
            'payment_method': 'transfer',
            'order_id': order_id,
            'amount': str(amount),
            'bank_info': {
                'bank': transfer_config.get('bank'),
                'account': transfer_config.get('account'),
                'name': transfer_config.get('name')
            },
            'payment_url': None,
            'payment_token': None,
            'expires_at': None
        }
    
    # Line Pay 相關方法
    async def create_linepay_order(self, order_id: str, amount: Decimal, customer_info: Dict) -> Dict[str, Any]:
        """建立 Line Pay 訂單"""
        linepay_config = self.settings.get('payment_linepay')
        if not linepay_config:
            raise ValueError("Line Pay 設定未設置")
        
        # Line Pay API 呼叫邏輯
        api_url = "https://sandbox-api-pay.line.me/v3/payments/request"
        
        headers = {
            'Content-Type': 'application/json',
            'X-LINE-ChannelId': linepay_config.get('channel_id'),
            'X-LINE-ChannelSecret': linepay_config.get('channel_secret')
        }
        
        payload = {
            'amount': int(amount),
            'currency': 'TWD',
            'orderId': order_id,
            'packages': [{
                'id': 'package1',
                'amount': int(amount),
                'products': [{
                    'name': f'訂單 {order_id}',
                    'quantity': 1,
                    'price': int(amount)
                }]
            }],
            'redirectUrls': {
                'confirmUrl': f'https://yourdomain.com/payment/linepay/confirm?orderId={order_id}',
                'cancelUrl': f'https://yourdomain.com/payment/linepay/cancel?orderId={order_id}'
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=payload)
            result = response.json()
            
            if result.get('returnCode') == '0000':
                return {
                    'payment_method': 'linepay',
                    'order_id': order_id,
                    'amount': str(amount),
                    'payment_url': result['info']['paymentUrl']['web'],
                    'payment_token': result['info']['transactionId'],
                    'expires_at': None
                }
            else:
                raise ValueError(f"Line Pay 建立訂單失敗: {result.get('returnMessage')}")
    
    # 綠界相關方法
    def create_ecpay_order(self, order_id: str, amount: Decimal, customer_info: Dict) -> Dict[str, Any]:
        """建立綠界訂單"""
        ecpay_config = self.settings.get('payment_ecpay')
        if not ecpay_config:
            raise ValueError("綠界設定未設置")
        
        # 綠界 API 參數
        api_url = ecpay_config.get('api_url', 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5')
        
        params = {
            'MerchantID': ecpay_config.get('merchant_id'),
            'MerchantTradeNo': order_id,
            'MerchantTradeDate': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'PaymentType': 'aio',
            'TotalAmount': int(amount),
            'TradeDesc': f'訂單 {order_id}',
            'ItemName': f'訂單 {order_id}',
            'ReturnURL': f'https://yourdomain.com/payment/ecpay/return',
            'ChoosePayment': 'ALL',
            'ClientBackURL': f'https://yourdomain.com/payment/ecpay/client_back?orderId={order_id}',
            'EncryptType': 1
        }
        
        # 產生檢查碼
        check_mac_value = self._generate_ecpay_check_mac_value(params, ecpay_config)
        params['CheckMacValue'] = check_mac_value
        
        return {
            'payment_method': 'ecpay',
            'order_id': order_id,
            'amount': str(amount),
            'payment_url': api_url,
            'payment_params': params,
            'payment_token': order_id,
            'expires_at': None
        }
    
    def _generate_ecpay_check_mac_value(self, params: Dict, config: Dict) -> str:
        """產生綠界檢查碼"""
        hash_key = config.get('hash_key')
        hash_iv = config.get('hash_iv')
        
        # 排序參數
        sorted_params = sorted(params.items())
        
        # 組合字串
        raw_string = f"HashKey={hash_key}&" + "&".join([f"{k}={v}" for k, v in sorted_params]) + f"&HashIV={hash_iv}"
        
        # URL encode
        raw_string = raw_string.replace("%", "%25").replace("~", "%7E")
        
        # SHA256 雜湊
        return hashlib.sha256(raw_string.encode()).hexdigest().upper()
    
    # PayPal 相關方法
    def create_paypal_order(self, order_id: str, amount: Decimal, customer_info: Dict) -> Dict[str, Any]:
        """建立 PayPal 訂單"""
        paypal_config = self.settings.get('payment_paypal')
        if not paypal_config:
            raise ValueError("PayPal 設定未設置")
        
        # 配置 PayPal SDK
        paypalrestsdk.configure({
            "mode": paypal_config.get('environment', 'sandbox'),
            "client_id": paypal_config.get('client_id'),
            "client_secret": paypal_config.get('client_secret')
        })
        
        # 建立付款
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"https://yourdomain.com/payment/paypal/return?orderId={order_id}",
                "cancel_url": f"https://yourdomain.com/payment/paypal/cancel?orderId={order_id}"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"訂單 {order_id}",
                        "sku": order_id,
                        "price": str(amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "description": f"訂單 {order_id} 付款"
            }]
        })
        
        if payment.create():
            # 取得付款 URL
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return {
                'payment_method': 'paypal',
                'order_id': order_id,
                'amount': str(amount),
                'payment_url': approval_url,
                'payment_token': payment.id,
                'expires_at': None
            }
        else:
            raise ValueError(f"PayPal 建立訂單失敗: {payment.error}")
    
    # 通用方法
    def create_payment_order(self, payment_method: str, order_id: str, amount: Decimal, customer_info: Dict) -> Dict[str, Any]:
        """建立付款訂單（通用入口）"""
        if payment_method == 'transfer':
            return self.create_transfer_order(order_id, amount, customer_info)
        elif payment_method == 'linepay':
            import asyncio
            return asyncio.run(self.create_linepay_order(order_id, amount, customer_info))
        elif payment_method == 'ecpay':
            return self.create_ecpay_order(order_id, amount, customer_info)
        elif payment_method == 'paypal':
            return self.create_paypal_order(order_id, amount, customer_info)
        else:
            raise ValueError(f"不支援的付款方式: {payment_method}")
    
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
        # Line Pay 付款確認邏輯
        linepay_config = self.settings.get('payment_linepay')
        transaction_id = payment_data.get('transactionId')
        
        api_url = f"https://sandbox-api-pay.line.me/v3/payments/{transaction_id}/confirm"
        
        headers = {
            'Content-Type': 'application/json',
            'X-LINE-ChannelId': linepay_config.get('channel_id'),
            'X-LINE-ChannelSecret': linepay_config.get('channel_secret')
        }
        
        payload = {
            'amount': payment_data.get('amount'),
            'currency': 'TWD'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=payload)
            result = response.json()
            
            return {
                'success': result.get('returnCode') == '0000',
                'message': result.get('returnMessage'),
                'transaction_id': transaction_id,
                'payment_data': result
            }
    
    def _verify_ecpay_payment(self, payment_data: Dict) -> Dict[str, Any]:
        """驗證綠界付款"""
        # 綠界付款驗證邏輯
        ecpay_config = self.settings.get('payment_ecpay')
        
        # 驗證檢查碼
        received_mac = payment_data.pop('CheckMacValue', '')
        calculated_mac = self._generate_ecpay_check_mac_value(payment_data, ecpay_config)
        
        success = received_mac == calculated_mac and payment_data.get('RtnCode') == '1'
        
        return {
            'success': success,
            'message': payment_data.get('RtnMsg', ''),
            'transaction_id': payment_data.get('TradeNo', ''),
            'payment_data': payment_data
        }
    
    def _verify_paypal_payment(self, payment_data: Dict) -> Dict[str, Any]:
        """驗證 PayPal 付款"""
        # PayPal 付款驗證邏輯
        paypal_config = self.settings.get('payment_paypal')
        
        paypalrestsdk.configure({
            "mode": paypal_config.get('environment', 'sandbox'),
            "client_id": paypal_config.get('client_id'),
            "client_secret": paypal_config.get('client_secret')
        })
        
        payment_id = payment_data.get('paymentId')
        payer_id = payment_data.get('PayerID')
        
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            return {
                'success': True,
                'message': '付款成功',
                'transaction_id': payment_id,
                'payment_data': payment.to_dict()
            }
        else:
            return {
                'success': False,
                'message': f'付款失敗: {payment.error}',
                'transaction_id': payment_id,
                'payment_data': payment.error
            }