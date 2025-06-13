#!/usr/bin/env python3
"""
建立測試數據腳本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import User, Product, Order, OrderItem, Post
from app.models.user import UserRole
from app.models.order import OrderStatus
from werkzeug.security import generate_password_hash

def create_test_users(db: Session):
    """建立測試用戶"""
    print("👤 建立測試用戶...")
    
    users_data = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "系統管理員",
            "role": UserRole.ADMIN
        },
        {
            "username": "john_doe",
            "email": "john@example.com", 
            "password": "password123",
            "full_name": "John Doe",
            "role": UserRole.USER
        },
        {
            "username": "jane_smith",
            "email": "jane@example.com",
            "password": "password123", 
            "full_name": "Jane Smith",
            "role": UserRole.USER
        }
    ]
    
    created_users = []
    for user_data in users_data:
        existing_user = db.query(User).filter(
            (User.username == user_data["username"]) | 
            (User.email == user_data["email"])
        ).first()
        
        if existing_user:
            print(f"   用戶 {user_data['username']} 已存在，跳過...")
            created_users.append(existing_user)
            continue
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password_hash=generate_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"]
        )
        db.add(user)
        created_users.append(user)
        print(f"   ✅ 建立用戶: {user_data['username']}")
    
    db.commit()
    return created_users

def create_test_products(db: Session):
    """建立測試商品"""
    print("🛍️ 建立測試商品...")
    
    products_data = [
        {
            "name": "iPhone 15 Pro Max",
            "description": "最新款 iPhone，搭載 A17 Pro 晶片，擁有絕佳的攝影功能和效能表現。",
            "short_description": "蘋果最新旗艦手機",
            "price": 39900,
            "sale_price": 35900,
            "stock_quantity": 50,
            "sku": "IPHONE15PM-001",
            "featured_image": "/static/images/iphone15.jpg",
            "is_active": True,
            "is_featured": True
        },
        {
            "name": "MacBook Air M3",
            "description": "全新 M3 晶片筆記型電腦，輕薄設計，強大效能，適合工作和娛樂。",
            "short_description": "蘋果輕薄筆電",
            "price": 35900,
            "stock_quantity": 30,
            "sku": "MBA-M3-001",
            "featured_image": "/static/images/macbook-air.jpg",
            "is_active": True,
            "is_featured": True
        },
        {
            "name": "時尚女裝外套",
            "description": "精緻設計的女性外套，適合春秋季節穿著，展現優雅風格。",
            "short_description": "時尚女性外套",
            "price": 2990,
            "sale_price": 2390,
            "stock_quantity": 25,
            "sku": "COAT-W-001",
            "featured_image": "/static/images/coat.jpg",
            "is_active": True,
            "is_featured": False
        },
        {
            "name": "北歐風餐桌",
            "description": "簡約北歐風格餐桌，實木材質，適合現代家居裝飾。",
            "short_description": "北歐實木餐桌", 
            "price": 15900,
            "stock_quantity": 15,
            "sku": "TABLE-001",
            "featured_image": "/static/images/table.jpg",
            "is_active": True,
            "is_featured": False
        },
        {
            "name": "天然保濕面霜",
            "description": "採用天然植物精華，深層滋潤肌膚，適合各種膚質使用。",
            "short_description": "天然植物面霜",
            "price": 899,
            "stock_quantity": 100,
            "sku": "CREAM-001",
            "featured_image": "/static/images/cream.jpg",
            "is_active": True,
            "is_featured": False
        },
        {
            "name": "專業運動鞋",
            "description": "專為運動設計的高性能鞋款，提供絕佳的支撐性和舒適度。",
            "short_description": "專業運動鞋款",
            "price": 3290,
            "sale_price": 2890,
            "stock_quantity": 45,
            "sku": "SHOES-001",
            "featured_image": "/static/images/shoes.jpg",
            "is_active": True,
            "is_featured": True
        }
    ]
    
    created_products = []
    for prod_data in products_data:
        existing_product = db.query(Product).filter(Product.sku == prod_data["sku"]).first()
        if existing_product:
            print(f"   商品 {prod_data['name']} 已存在，跳過...")
            created_products.append(existing_product)
            continue
        
        product = Product(
            name=prod_data["name"],
            description=prod_data["description"],
            short_description=prod_data["short_description"],
            price=prod_data["price"],
            sale_price=prod_data.get("sale_price"),
            stock_quantity=prod_data["stock_quantity"],
            sku=prod_data["sku"],
            featured_image=prod_data["featured_image"],
            is_active=prod_data["is_active"],
            is_featured=prod_data["is_featured"]
        )
        product.slug = product.generate_slug(prod_data["name"])
        
        db.add(product)
        created_products.append(product)
        print(f"   ✅ 建立商品: {prod_data['name']}")
    
    db.commit()
    return created_products

def create_test_posts(db: Session):
    """建立測試文章"""
    print("📝 建立測試文章...")
    
    posts_data = [
        {
            "title": "2024年科技趨勢回顧",
            "content": "回顧2024年最重要的科技發展，包括人工智能、區塊鏈技術和可持續能源的突破。",
            "excerpt": "深入分析2024年科技領域的重大變革和未來展望。",
            "featured_image": "/static/images/tech-trends.jpg",
            "is_published": True
        },
        {
            "title": "居家生活美學指南",
            "content": "如何打造舒適且美觀的居家環境，從色彩搭配到家具選擇的完整指南。",
            "excerpt": "打造理想居家環境的實用建議和設計靈感。",
            "featured_image": "/static/images/home-design.jpg",
            "is_published": True
        },
        {
            "title": "線上購物安全指南",
            "content": "在數位時代如何安全地進行線上購物，保護個人資訊和財務安全的重要提醒。",
            "excerpt": "保障線上購物安全的必備知識和實用技巧。",
            "featured_image": "/static/images/online-safety.jpg",
            "is_published": False
        }
    ]
    
    created_posts = []
    for post_data in posts_data:
        existing_post = db.query(Post).filter(Post.title == post_data["title"]).first()
        if existing_post:
            print(f"   文章 {post_data['title']} 已存在，跳過...")
            created_posts.append(existing_post)
            continue
        
        post = Post(
            title=post_data["title"],
            content=post_data["content"],
            excerpt=post_data["excerpt"],
            featured_image=post_data["featured_image"],
            is_published=post_data["is_published"]
        )
        post.slug = post.generate_slug(post_data["title"])
        
        db.add(post)
        created_posts.append(post)
        print(f"   ✅ 建立文章: {post_data['title']}")
    
    db.commit()
    return created_posts

def create_test_orders(db: Session, users, products):
    """建立測試訂單"""
    print("🛒 建立測試訂單...")
    
    orders_data = [
        {
            "user": users[1],  # john_doe
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "0912345678",
            "shipping_address": "台北市信義區信義路五段7號",
            "items": [
                {"product": products[0], "quantity": 1, "price": products[0].price},
                {"product": products[1], "quantity": 1, "price": products[1].price}
            ]
        },
        {
            "user": users[2],  # jane_smith
            "customer_name": "Jane Smith", 
            "customer_email": "jane@example.com",
            "customer_phone": "0987654321",
            "shipping_address": "高雄市前金區中正四路211號",
            "items": [
                {"product": products[2], "quantity": 2, "price": products[2].sale_price or products[2].price}
            ]
        }
    ]
    
    created_orders = []
    for order_data in orders_data:
        # 計算訂單總金額
        total_amount = sum(item["price"] * item["quantity"] for item in order_data["items"])
        
        order = Order(
            user_id=order_data["user"].id,
            order_number=f"ORD{len(created_orders) + 1:06d}",
            customer_name=order_data["customer_name"],
            customer_email=order_data["customer_email"],
            customer_phone=order_data["customer_phone"],
            shipping_address=order_data["shipping_address"],
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        
        db.add(order)
        db.flush()  # 取得 order.id
        
        # 建立訂單項目
        for item_data in order_data["items"]:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                quantity=item_data["quantity"],
                price=item_data["price"]
            )
            db.add(order_item)
        
        created_orders.append(order)
        print(f"   ✅ 建立訂單: {order.order_number}")
    
    db.commit()
    return created_orders

def main():
    """主函數"""
    print("🚀 開始建立測試數據...")
    
    # 建立資料庫連接
    db = next(get_db())
    
    try:
        # 建立測試數據
        users = create_test_users(db)
        products = create_test_products(db)
        posts = create_test_posts(db)
        orders = create_test_orders(db, users, products)
        
        # 統計
        print("\n📊 測試數據建立完成！")
        print(f"   👤 用戶: {len(users)} 個")
        print(f"   🛍️ 商品: {len(products)} 個")
        print(f"   📝 文章: {len(posts)} 個")
        print(f"   🛒 訂單: {len(orders)} 個")
        print("\n✅ 所有測試數據已成功建立！")
        
    except Exception as e:
        print(f"❌ 建立測試數據時發生錯誤: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 