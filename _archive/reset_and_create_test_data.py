#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置數據庫並建立全新測試數據

測試資料規格：
- 10 個部落格圖文（2 個分類）
- 30 個商品（4 個分類）
- 8 個會員
- 20 張訂單
"""

import os
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from faker import Faker
from decimal import Decimal

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import (
    User, Post, Product, Order, OrderItem, 
    PageView, NewsletterSubscriber, Favorite, UserRole, OrderStatus
)
from app.auth import get_password_hash
from app.config import settings

# 初始化 Faker
fake = Faker('zh_TW')

def drop_all_tables():
    """刪除所有資料表"""
    print("🗑️  正在清除所有現有數據...")
    Base.metadata.drop_all(bind=engine)
    print("✅ 所有資料表已清除")

def create_all_tables():
    """建立所有資料表"""
    print("📊 正在建立資料表結構...")
    Base.metadata.create_all(bind=engine)
    print("✅ 資料表結構已建立")

def create_admin_user(db: Session):
    """建立管理員帳號"""
    print("👑 正在建立管理員帳號...")
    
    admin = User(
        username=settings.admin_username,
        email=settings.admin_email,
        full_name=settings.admin_full_name,
        hashed_password=get_password_hash(settings.admin_password),
        is_active=True,
        role=UserRole.ADMIN
    )
    
    db.add(admin)
    db.commit()
    print(f"✅ 管理員帳號已建立: {settings.admin_username}")
    return admin

def create_users(db: Session):
    """建立會員（8個）"""
    print("👥 正在建立會員帳號...")
    
    users = []
    for i in range(8):
        user = User(
            username=f"user{i+1:02d}",
            email=fake.email(),
            full_name=fake.name(),
            hashed_password=get_password_hash("password123"),
            is_active=True,
            role=UserRole.USER,
            phone=fake.phone_number(),
            address=fake.address()
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✅ 已建立 {len(users)} 個會員帳號")
    return users

def create_blog_posts(db: Session, admin_user):
    """建立部落格文章（5篇）"""
    print("📝 正在建立部落格文章...")
    
    posts_data = [
        {
            "title": "2024年人工智慧發展趨勢",
            "content": """# 2024年人工智慧發展趨勢

人工智慧在2024年持續快速發展，以下是主要趨勢：

## 1. 生成式AI的普及
ChatGPT、Claude等大型語言模型已經改變了我們的工作方式。

## 2. AI與日常生活的深度整合
從智慧家居到自動駕駛，AI正在改變我們的生活。

## 結論
AI技術的發展將持續加速，我們需要持續學習適應這個變化。""",
            "excerpt": "探討2024年AI發展的主要趨勢和應用場景"
        },
        {
            "title": "5G技術如何改變我們的連接方式",
            "content": """# 5G技術如何改變我們的連接方式

5G技術的普及正在重新定義我們的連接體驗。

## 超高速傳輸
- 下載速度可達1Gbps以上
- 延遲降至1毫秒以下

## 物聯網革命
5G讓更多設備能夠同時連接，推動智慧城市發展。""",
            "excerpt": "分析5G技術對各行業的影響和未來發展"
        },
        {
            "title": "電商平台優化指南",
            "content": """# 電商平台優化指南

想要提升電商平台的轉換率？以下是一些實用的優化技巧。

## 1. 提升網站速度
快速的載入時間是提升用戶體驗的關鍵。

## 2. 優化商品頁面
清晰的商品描述和高品質圖片能提升購買意願。""",
            "excerpt": "電商平台優化的實用技巧和策略"
        },
        {
            "title": "居家辦公效率提升指南",
            "content": """# 居家辦公效率提升指南

居家辦公已成為新常態，如何在家中保持高效工作？

## 環境設置
- 獨立的工作空間
- 良好的照明
- 舒適的座椅

## 時間管理
建立明確的工作時間表，避免工作與生活混淆。""",
            "excerpt": "居家辦公的效率提升方法和技巧"
        },
        {
            "title": "健康生活的數位化管理",
            "content": """# 健康生活的數位化管理

科技如何幫助我們維持健康的生活方式？

## 健康監測APP
利用智慧型手機監測步數、心率等健康指標。

## 線上健身課程
疫情期間，線上健身成為新趨勢。""",
            "excerpt": "如何利用科技工具管理個人健康"
        }
    ]
    
    posts = []
    for i, post_data in enumerate(posts_data):
        post = Post(
            title=post_data["title"],
            content=post_data["content"],
            excerpt=post_data["excerpt"],
            is_published=True
        )
        db.add(post)
        posts.append(post)
    
    db.commit()
    print(f"✅ 已建立 {len(posts)} 篇部落格文章")
    return posts

def create_products(db: Session):
    """建立商品（12個）"""
    print("🛍️ 正在建立商品...")
    
    products_data = [
        # 3C數位商品
        {"name": "無線藍牙耳機", "price": 2999, "sale_price": 2499, "stock": 50},
        {"name": "智能手環", "price": 1999, "sale_price": None, "stock": 30},
        {"name": "無線充電器", "price": 999, "sale_price": 799, "stock": 40},
        
        # 居家生活
        {"name": "多功能收納盒", "price": 599, "sale_price": None, "stock": 100},
        {"name": "香氛蠟燭", "price": 399, "sale_price": 299, "stock": 60},
        {"name": "保溫水杯", "price": 799, "sale_price": None, "stock": 80},
        
        # 運動健身
        {"name": "瑜珈墊", "price": 1299, "sale_price": 999, "stock": 25},
        {"name": "運動水壺", "price": 499, "sale_price": None, "stock": 70},
        {"name": "健身彈力帶", "price": 399, "sale_price": 299, "stock": 90},
        
        # 美妝保養
        {"name": "保濕面膜", "price": 299, "sale_price": None, "stock": 200},
        {"name": "防曬乳", "price": 899, "sale_price": 699, "stock": 120},
        {"name": "護手霜", "price": 199, "sale_price": None, "stock": 150}
    ]
    
    products = []
    for i, product_data in enumerate(products_data):
        product = Product(
            name=product_data["name"],
            description=f"這是{product_data['name']}的詳細描述。高品質材料製作，物超所值。",
            short_description=f"優質{product_data['name']}，限時優惠中！",
            price=Decimal(str(product_data["price"])),
            sale_price=Decimal(str(product_data["sale_price"])) if product_data["sale_price"] else None,
            stock_quantity=product_data["stock"],
            sku=f"SKU{i+1:03d}",
            is_active=True,
            is_featured=i < 6  # 前6個商品設為精選
        )
        db.add(product)
        products.append(product)
    
    db.commit()
    print(f"✅ 已建立 {len(products)} 個商品")
    return products

def create_orders(db: Session, users, products):
    """建立訂單（15筆）"""
    print("📦 正在建立訂單...")
    
    orders = []
    for i in range(15):
        user = random.choice(users)
        order = Order(
            order_number=f"ORD{i+1:06d}",
            user_id=user.id,
            customer_name=user.full_name,
            customer_email=user.email,
            customer_phone=user.phone or fake.phone_number(),
            shipping_address=user.address or fake.address(),
            status=random.choice([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
        )
        
        # 為每個訂單添加1-3個商品
        selected_products = random.sample(products, random.randint(1, 3))
        total_amount = Decimal('0')
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            price = product.sale_price if product.sale_price else product.price
            
            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                product_price=price,
                quantity=quantity
            )
            order.items.append(order_item)
            total_amount += price * quantity
        
        order.subtotal = total_amount
        order.total_amount = total_amount
        
        db.add(order)
        orders.append(order)
    
    db.commit()
    print(f"✅ 已建立 {len(orders)} 筆訂單")
    return orders

def create_analytics_data(db: Session):
    """建立分析資料"""
    print("📊 正在建立分析資料...")
    
    # 建立頁面瀏覽記錄
    page_views = []
    pages = ["/", "/blog", "/shop", "/about", "/contact"]
    
    for _ in range(200):
        page_view = PageView(
            page_url=random.choice(pages),
            page_type="general",
            user_agent=fake.user_agent(),
            visitor_ip=fake.ipv4()
        )
        page_views.append(page_view)
    
    db.add_all(page_views)
    db.commit()
    print(f"✅ 已建立 {len(page_views)} 筆頁面瀏覽記錄")

def main():
    """主要執行函數"""
    try:
        print("🚀 開始重置資料庫並建立測試資料...")
        
        # 1. 重置資料庫
        drop_all_tables()
        create_all_tables()
        
        # 2. 建立資料
        db = SessionLocal()
        try:
            admin_user = create_admin_user(db)
            users = create_users(db)
            posts = create_blog_posts(db, admin_user)
            products = create_products(db)
            orders = create_orders(db, users, products)
            create_analytics_data(db)
            
            print("\n🎉 資料庫重置和測試資料建立完成！")
            print(f"   👑 管理員帳號: {admin_user.username} / {settings.admin_password}")
            print(f"   👥 會員數: {len(users)}")
            print(f"   📝 文章數: {len(posts)}")
            print(f"   🛍️ 商品數: {len(products)}")
            print(f"   📦 訂單數: {len(orders)}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()