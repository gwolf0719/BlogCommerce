#!/usr/bin/env python3
"""
大量模擬使用者下單腳本
"""

import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

# 添加專案路徑
sys.path.append('.')

from app.database import SessionLocal
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User


# 模擬的客戶資料
FAKE_CUSTOMERS = [
    {"name": "王小明", "email": "wang.ming@email.com", "phone": "0912345678"},
    {"name": "李美麗", "email": "li.beauty@email.com", "phone": "0923456789"},
    {"name": "張大偉", "email": "zhang.david@email.com", "phone": "0934567890"},
    {"name": "陳小芳", "email": "chen.fang@email.com", "phone": "0945678901"},
    {"name": "林志明", "email": "lin.ming@email.com", "phone": "0956789012"},
    {"name": "黃淑芬", "email": "huang.fen@email.com", "phone": "0967890123"},
    {"name": "吳建華", "email": "wu.hua@email.com", "phone": "0978901234"},
    {"name": "劉雅婷", "email": "liu.ting@email.com", "phone": "0989012345"},
    {"name": "蔡志偉", "email": "tsai.wei@email.com", "phone": "0990123456"},
    {"name": "許美惠", "email": "hsu.hui@email.com", "phone": "0901234567"},
]

# 模擬的地址
FAKE_ADDRESSES = [
    "台北市中正區忠孝東路一段1號",
    "台北市大安區敦化南路二段2號",
    "台北市信義區松仁路3號",
    "新北市板橋區中山路一段4號",
    "新北市新莊區思源路5號",
    "桃園市桃園區中正路6號",
    "台中市西屯區文心路7號",
    "台南市東區東門路8號",
    "高雄市前金區中正四路9號",
    "台北市士林區文林路10號",
]


def generate_order_number() -> str:
    """生成訂單編號"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = random.randint(100000, 999999)
    return f"ORD{random_part}"


def get_active_products(db) -> List[Product]:
    """獲取所有啟用的商品"""
    return db.query(Product).filter(Product.is_active == True).all()


def get_random_user(db) -> User:
    """隨機獲取一個用戶，如果沒有則返回None（模擬訪客購買）"""
    from app.models.user import UserRole
    users = db.query(User).filter(User.role == UserRole.USER).limit(10).all()
    
    if users and random.choice([True, False]):  # 50% 機率是會員購買
        return random.choice(users)
    return None


def calculate_shipping_fee(total_amount: Decimal) -> Decimal:
    """計算運費"""
    if total_amount >= 1000:
        return Decimal("0")  # 滿1000免運費
    else:
        return Decimal("100")  # 運費100元


def create_random_order(db, products: List[Product]) -> Order:
    """創建一個隨機訂單"""
    # 隨機選擇客戶資料
    customer = random.choice(FAKE_CUSTOMERS)
    address = random.choice(FAKE_ADDRESSES)
    
    # 隨機選擇是否為會員
    user = get_random_user(db)
    
    # 隨機選擇商品（1-5個商品）
    num_items = random.randint(1, min(5, len(products)))
    selected_products = random.sample(products, num_items)
    
    # 計算訂單總額
    subtotal = Decimal("0")
    order_items_data = []
    
    for product in selected_products:
        quantity = random.randint(1, 3)
        price = product.current_price
        item_total = price * quantity
        subtotal += item_total
        
        order_items_data.append({
            "product": product,
            "quantity": quantity,
            "price": price,
            "total": item_total
        })
    
    # 計算運費和總額
    shipping_fee = calculate_shipping_fee(subtotal)
    total_amount = subtotal + shipping_fee
    
    # 創建訂單
    order = Order(
        order_number=generate_order_number(),
        user_id=user.id if user else None,
        customer_name=customer["name"],
        customer_email=customer["email"],
        customer_phone=customer["phone"],
        shipping_address=address,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total_amount=total_amount,
        status=random.choice(list(OrderStatus)),
        notes=random.choice([
            None,
            "請儘快出貨",
            "希望包裝精美一點",
            "如果沒有現貨請取消訂單",
            "送貨前請先電話聯絡"
        ])
    )
    
    db.add(order)
    db.flush()  # 獲取訂單ID
    
    # 創建訂單項目
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            product_name=item_data["product"].name,
            product_price=item_data["price"],
            quantity=item_data["quantity"]
        )
        db.add(order_item)
    
    return order


def simulate_orders(num_orders: int = 50):
    """模擬大量訂單"""
    print(f"🚀 開始模擬 {num_orders} 個訂單...")
    
    db = SessionLocal()
    try:
        # 獲取所有啟用的商品
        products = get_active_products(db)
        
        if not products:
            print("❌ 沒有找到啟用的商品，無法創建訂單")
            return
        
        print(f"📦 找到 {len(products)} 個可購買商品")
        
        # 批量創建訂單
        created_orders = []
        
        for i in range(num_orders):
            try:
                order = create_random_order(db, products)
                created_orders.append(order)
                
                if (i + 1) % 10 == 0:
                    print(f"✅ 已創建 {i + 1} 個訂單...")
                    
            except Exception as e:
                print(f"❌ 創建第 {i + 1} 個訂單時發生錯誤: {e}")
                continue
        
        # 提交所有變更
        db.commit()
        print(f"🎉 成功創建 {len(created_orders)} 個模擬訂單！")
        
        # 顯示統計信息
        total_amount = sum(order.total_amount for order in created_orders)
        avg_amount = total_amount / len(created_orders) if created_orders else 0
        
        print(f"\n📊 訂單統計:")
        print(f"   總訂單數: {len(created_orders)}")
        print(f"   總金額: NT$ {total_amount:,.2f}")
        print(f"   平均訂單金額: NT$ {avg_amount:,.2f}")
        
        # 按狀態統計
        status_counts = {}
        for order in created_orders:
            status = order.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📈 訂單狀態分布:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} 個")
            
    except Exception as e:
        db.rollback()
        print(f"❌ 模擬訂單時發生錯誤: {e}")
        raise
    finally:
        db.close()


def clear_test_orders():
    """清除測試訂單（可選功能）"""
    response = input("⚠️  是否要清除所有現有訂單？(y/N): ")
    if response.lower() != 'y':
        return
    
    db = SessionLocal()
    try:
        # 刪除所有訂單項目
        db.execute("DELETE FROM order_items")
        # 刪除所有訂單
        db.execute("DELETE FROM orders")
        db.commit()
        print("🗑️  所有訂單已清除")
    except Exception as e:
        db.rollback()
        print(f"❌ 清除訂單時發生錯誤: {e}")
    finally:
        db.close()


def main():
    """主函數"""
    print("🛍️  模擬大量使用者下單工具")
    print("=" * 50)
    
    try:
        # 詢問是否清除現有訂單
        clear_choice = input("是否要先清除現有的測試訂單？(y/N): ")
        if clear_choice.lower() == 'y':
            clear_test_orders()
        
        # 詢問要創建的訂單數量
        while True:
            try:
                num_orders = input("請輸入要創建的訂單數量 (預設: 50): ").strip()
                if not num_orders:
                    num_orders = 50
                else:
                    num_orders = int(num_orders)
                
                if num_orders <= 0:
                    print("❌ 訂單數量必須大於 0")
                    continue
                
                if num_orders > 1000:
                    print("⚠️  訂單數量過多，建議不超過 1000 個")
                    confirm = input("是否繼續？(y/N): ")
                    if confirm.lower() != 'y':
                        continue
                
                break
                
            except ValueError:
                print("❌ 請輸入有效的數字")
        
        # 開始模擬
        simulate_orders(num_orders)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  用戶中斷操作")
    except Exception as e:
        print(f"\n❌ 程式執行時發生錯誤: {e}")


if __name__ == "__main__":
    main() 