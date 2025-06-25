#!/usr/bin/env python3
"""
金流功能展示腳本
展示 BlogCommerce 金流系統的完整功能
"""

import asyncio
import json
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.settings import SystemSettings
from app.models.order import Order, OrderStatus, PaymentStatus, PaymentMethod
from app.models.user import User
from app.models.product import Product
from app.services.payment_service import PaymentService


def setup_demo_data():
    """設置展示用的測試資料"""
    db = SessionLocal()
    
    try:
        print("🔧 設置展示用測試資料...")
        
        # 清理舊資料
        db.query(SystemSettings).filter(SystemSettings.category == "payment").delete()
        
        # 設置金流配置
        payment_configs = [
            {
                "key": "payment_transfer",
                "value": {
                    "bank": "國泰世華銀行",
                    "account": "1234567890",
                    "name": "BlogCommerce 商店"
                },
                "description": "轉帳金流設定"
            },
            {
                "key": "payment_linepay",
                "value": {
                    "channel_id": "1234567890",
                    "channel_secret": "abcdef1234567890",
                    "store_name": "BlogCommerce 線上商店"
                },
                "description": "Line Pay 金流設定"
            },
            {
                "key": "payment_ecpay",
                "value": {
                    "merchant_id": "2000132",
                    "hash_key": "5294y06JbISpM5x9",
                    "hash_iv": "v77hoKGq4kWxNNIS",
                    "api_url": "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
                },
                "description": "綠界金流設定"
            },
            {
                "key": "payment_paypal",
                "value": {
                    "client_id": "AYSq3RDGsmBLJE-otTkBtM-jBRd1TCQwFf9RGfwddNXWz0uFU9ztymylOhRS",
                    "client_secret": "EGnHDxD_qRPdaLdHi7__jLS3rD7yOo-FPcbgJl6RKqgMbm6BG9aQn5Eq7PW2",
                    "environment": "sandbox"
                },
                "description": "PayPal 金流設定"
            }
        ]
        
        for config in payment_configs:
            setting = SystemSettings(
                key=config["key"],
                value=json.dumps(config["value"]),
                data_type="json",
                category="payment",
                description=config["description"]
            )
            db.add(setting)
        
        # 建立測試商品
        test_product = Product(
            name="經典白T恤",
            description="高品質純棉白色T恤，適合日常穿著",
            price=Decimal("599.00"),
            sale_price=Decimal("399.00"),
            stock_quantity=50,
            is_active=True
        )
        db.add(test_product)
        
        db.commit()
        print("✅ 測試資料設置完成")
        return test_product.id
        
    finally:
        db.close()


def demo_payment_settings():
    """展示金流設定功能"""
    print("\n📋 金流設定展示")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 查詢所有金流設定
        payment_settings = db.query(SystemSettings).filter(
            SystemSettings.category == "payment"
        ).all()
        
        for setting in payment_settings:
            print(f"\n🔧 {setting.description}")
            print(f"   Key: {setting.key}")
            try:
                value = json.loads(setting.value)
                for k, v in value.items():
                    if 'secret' in k.lower() or 'key' in k.lower():
                        print(f"   {k}: {'*' * len(str(v))}")
                    else:
                        print(f"   {k}: {v}")
            except:
                print(f"   Value: {setting.value}")
    
    finally:
        db.close()


def demo_payment_creation():
    """展示付款訂單建立"""
    print("\n💳 付款訂單建立展示")
    print("=" * 50)
    
    with PaymentService() as payment_service:
        test_cases = [
            {
                "method": "transfer",
                "name": "轉帳付款",
                "order_id": f"DEMO_TRANSFER_{datetime.now().strftime('%H%M%S')}"
            },
            {
                "method": "linepay",
                "name": "Line Pay",
                "order_id": f"DEMO_LINEPAY_{datetime.now().strftime('%H%M%S')}"
            },
            {
                "method": "ecpay",
                "name": "綠界金流",
                "order_id": f"DEMO_ECPAY_{datetime.now().strftime('%H%M%S')}"
            },
            {
                "method": "paypal",
                "name": "PayPal",
                "order_id": f"DEMO_PAYPAL_{datetime.now().strftime('%H%M%S')}"
            }
        ]
        
        customer_info = {
            'name': '王小明',
            'email': 'demo@example.com',
            'phone': '0912345678'
        }
        
        for test_case in test_cases:
            try:
                print(f"\n🧪 測試 {test_case['name']} ({test_case['method']})")
                
                if test_case['method'] == 'linepay':
                    # Line Pay 需要 async 處理
                    result = asyncio.run(payment_service.create_linepay_order(
                        test_case['order_id'],
                        Decimal('399.00'),
                        customer_info
                    ))
                else:
                    result = payment_service.create_payment_order(
                        test_case['method'],
                        test_case['order_id'],
                        Decimal('399.00'),
                        customer_info
                    )
                
                print("✅ 付款訂單建立成功")
                print(f"   訂單編號: {result['order_id']}")
                print(f"   金額: ${result['amount']}")
                print(f"   付款方式: {result['payment_method']}")
                
                if result.get('payment_url'):
                    print(f"   付款連結: {result['payment_url'][:50]}...")
                
                if result.get('bank_info'):
                    bank_info = result['bank_info']
                    print(f"   銀行資訊: {bank_info['bank']} {bank_info['account']}")
                
            except Exception as e:
                print(f"❌ {test_case['name']} 測試失敗: {e}")


def demo_order_with_payment(product_id):
    """展示訂單與金流整合"""
    print("\n🛒 訂單與金流整合展示")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 建立測試訂單
        order_number = f"DEMO_ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order = Order(
            order_number=order_number,
            customer_name="張小華",
            customer_email="demo2@example.com",
            customer_phone="0987654321",
            shipping_address="台北市信義區信義路五段7號",
            subtotal=Decimal("399.00"),
            shipping_fee=Decimal("60.00"),
            total_amount=Decimal("459.00"),
            status=OrderStatus.PENDING,
            payment_method=PaymentMethod.TRANSFER,
            payment_status=PaymentStatus.UNPAID
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        print(f"📦 建立示範訂單")
        print(f"   訂單編號: {order.order_number}")
        print(f"   客戶姓名: {order.customer_name}")
        print(f"   總金額: ${order.total_amount}")
        print(f"   付款方式: {order.payment_method.value}")
        print(f"   付款狀態: {order.payment_status.value}")
        
        # 建立付款訂單
        print(f"\n💰 為訂單建立付款...")
        
        with PaymentService() as payment_service:
            payment_data = payment_service.create_transfer_order(
                order.order_number,
                order.total_amount,
                {
                    'name': order.customer_name,
                    'email': order.customer_email,
                    'phone': order.customer_phone
                }
            )
            
            # 更新訂單付款資訊
            order.payment_info = json.dumps(payment_data)
            order.payment_status = PaymentStatus.PENDING
            order.payment_updated_at = datetime.now()
            
            db.commit()
            
            print("✅ 付款訂單建立成功")
            print(f"   付款方式: {payment_data['payment_method']}")
            bank_info = payment_data['bank_info']
            print(f"   轉帳銀行: {bank_info['bank']}")
            print(f"   轉帳帳號: {bank_info['account']}")
            print(f"   轉帳戶名: {bank_info['name']}")
        
        return order.order_number
        
    finally:
        db.close()


def demo_manual_payment_confirmation(order_number):
    """展示手動付款確認"""
    print("\n✋ 手動付款確認展示")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 查找訂單
        order = db.query(Order).filter(Order.order_number == order_number).first()
        
        if order:
            print(f"📋 確認付款前狀態")
            print(f"   訂單編號: {order.order_number}")
            print(f"   付款狀態: {order.payment_status.value}")
            
            # 模擬管理員手動確認付款
            print(f"\n👨‍💼 管理員手動確認付款...")
            
            order.payment_status = PaymentStatus.PAID
            order.payment_updated_at = datetime.now()
            
            # 更新付款資訊
            payment_info = json.loads(order.payment_info) if order.payment_info else {}
            payment_info.update({
                'manual_confirmed': True,
                'confirmed_by': 'admin_demo',
                'confirmed_at': datetime.now().isoformat(),
                'notes': '展示用手動確認付款'
            })
            order.payment_info = json.dumps(payment_info)
            
            db.commit()
            
            print("✅ 付款確認完成")
            print(f"   付款狀態: {order.payment_status.value}")
            print(f"   確認時間: {order.payment_updated_at}")
        
    finally:
        db.close()


def demo_payment_statistics():
    """展示付款統計"""
    print("\n📊 付款統計展示")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 統計各種付款狀態的訂單
        payment_stats = {}
        for status in PaymentStatus:
            count = db.query(Order).filter(Order.payment_status == status).count()
            payment_stats[status.value] = count
        
        print("💳 付款狀態統計:")
        for status, count in payment_stats.items():
            print(f"   {status}: {count} 筆")
        
        # 統計各種付款方式
        method_stats = {}
        for method in PaymentMethod:
            count = db.query(Order).filter(Order.payment_method == method).count()
            method_stats[method.value] = count
        
        print("\n🏦 付款方式統計:")
        for method, count in method_stats.items():
            print(f"   {method}: {count} 筆")
        
        # 計算總營業額
        total_revenue = db.query(Order).filter(
            Order.payment_status == PaymentStatus.PAID
        ).with_entities(Order.total_amount).all()
        
        total = sum([order.total_amount for order in total_revenue])
        print(f"\n💰 總營業額: ${total}")
        
    finally:
        db.close()


def main():
    """主要展示流程"""
    print("🎉 BlogCommerce 金流系統展示")
    print("=" * 60)
    
    try:
        # 1. 設置測試資料
        product_id = setup_demo_data()
        
        # 2. 展示金流設定
        demo_payment_settings()
        
        # 3. 展示付款訂單建立
        demo_payment_creation()
        
        # 4. 展示訂單與金流整合
        order_number = demo_order_with_payment(product_id)
        
        # 5. 展示手動付款確認
        demo_manual_payment_confirmation(order_number)
        
        # 6. 展示付款統計
        demo_payment_statistics()
        
        print("\n🎊 金流系統展示完成！")
        print("\n📝 系統功能摘要:")
        print("   ✅ 支援 4 種金流方式：轉帳、Line Pay、綠界、PayPal")
        print("   ✅ 自動金流處理：訂單建立時自動建立付款")
        print("   ✅ 手動金流處理：管理員可手動確認付款")
        print("   ✅ 完整的付款狀態管理")
        print("   ✅ 金流設定管理介面")
        print("   ✅ 付款統計和報表功能")
        
    except Exception as e:
        print(f"❌ 展示過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()