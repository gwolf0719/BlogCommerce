#!/usr/bin/env python3
"""
建立測試資料腳本
創建多個用戶、商品和訂單來測試系統
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random

# 將 app 目錄加入 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, init_db
from app.models import User, Product, Category, Tag, Order, OrderItem, Post
from app.schemas.user import UserRole
from app.auth import get_password_hash
from sqlalchemy.orm import Session

def create_test_users(db: Session):
    """建立測試用戶"""
    print("🧑‍💼 建立測試用戶...")
    
    test_users = [
        {
            "username": "user001", 
            "email": "user001@test.com", 
            "password": "password123",
            "full_name": "張小明",
            "role": UserRole.USER
        },
        {
            "username": "user002", 
            "email": "user002@test.com", 
            "password": "password123",
            "full_name": "李小華",
            "role": UserRole.USER
        },
        {
            "username": "user003", 
            "email": "user003@test.com", 
            "password": "password123",
            "full_name": "王小美",
            "role": UserRole.USER
        },
        {
            "username": "user004", 
            "email": "user004@test.com", 
            "password": "password123",
            "full_name": "陳小強",
            "role": UserRole.USER
        },
        {
            "username": "user005", 
            "email": "user005@test.com", 
            "password": "password123",
            "full_name": "林小芳",
            "role": UserRole.USER
        },
        {
            "username": "demo", 
            "email": "demo@test.com", 
            "password": "demo123",
            "full_name": "演示帳號",
            "role": UserRole.USER
        },
        {
            "username": "test", 
            "email": "test@test.com", 
            "password": "test123",
            "full_name": "測試帳號",
            "role": UserRole.USER
        },
    ]
    
    created_users = []
    for user_data in test_users:
        # 檢查用戶是否已存在
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"   用戶 {user_data['email']} 已存在，跳過...")
            created_users.append(existing_user)
            continue
            
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=get_password_hash(user_data["password"]),
            role=user_data["role"],
            is_active=True
        )
        db.add(user)
        created_users.append(user)
        print(f"   ✅ 建立用戶: {user_data['email']} (密碼: {user_data['password']})")
    
    db.commit()
    return created_users

def create_test_categories(db: Session):
    """建立測試分類"""
    print("📁 建立商品分類...")
    
    categories_data = [
        {"name": "電子產品", "slug": "electronics", "description": "各種電子產品和數位設備", "type": "PRODUCT"},
        {"name": "服飾配件", "slug": "fashion", "description": "時尚服飾和配件商品", "type": "PRODUCT"},
        {"name": "居家生活", "slug": "home", "description": "居家用品和生活必需品", "type": "PRODUCT"},
        {"name": "美妝保養", "slug": "beauty", "description": "美妝化妝品和保養用品", "type": "PRODUCT"},
        {"name": "運動健身", "slug": "sports", "description": "運動器材和健身用品", "type": "PRODUCT"},
        {"name": "科技新知", "slug": "technology", "description": "科技新聞和產品評測", "type": "BLOG"},
        {"name": "生活分享", "slug": "lifestyle", "description": "生活心得和經驗分享", "type": "BLOG"},
        {"name": "購物指南", "slug": "shopping", "description": "購物心得和商品推薦", "type": "BLOG"},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        existing_cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if existing_cat:
            print(f"   分類 {cat_data['name']} 已存在，跳過...")
            created_categories.append(existing_cat)
            continue
            
        category = Category(
            name=cat_data["name"],
            slug=cat_data["slug"],
            description=cat_data["description"],
            type=cat_data["type"]
        )
        db.add(category)
        created_categories.append(category)
        print(f"   ✅ 建立分類: {cat_data['name']}")
    
    db.commit()
    return created_categories

def create_test_tags(db: Session):
    """建立測試標籤"""
    print("🏷️ 建立商品標籤...")
    
    tags_data = [
        {"name": "熱銷", "slug": "hot", "description": "熱銷商品", "type": "PRODUCT"},
        {"name": "新品", "slug": "new", "description": "新上市商品", "type": "PRODUCT"},
        {"name": "特價", "slug": "sale", "description": "特價優惠商品", "type": "PRODUCT"},
        {"name": "推薦", "slug": "recommended", "description": "編輯推薦商品", "type": "PRODUCT"},
        {"name": "限量", "slug": "limited", "description": "限量商品", "type": "PRODUCT"},
        {"name": "實用", "slug": "practical", "description": "實用好物", "type": "BLOG"},
        {"name": "評測", "slug": "review", "description": "商品評測文章", "type": "BLOG"},
        {"name": "教學", "slug": "tutorial", "description": "使用教學文章", "type": "BLOG"},
    ]
    
    created_tags = []
    for tag_data in tags_data:
        existing_tag = db.query(Tag).filter(Tag.slug == tag_data["slug"]).first()
        if existing_tag:
            print(f"   標籤 {tag_data['name']} 已存在，跳過...")
            created_tags.append(existing_tag)
            continue
            
        tag = Tag(
            name=tag_data["name"],
            slug=tag_data["slug"],
            description=tag_data["description"],
            type=tag_data["type"]
        )
        db.add(tag)
        created_tags.append(tag)
        print(f"   ✅ 建立標籤: {tag_data['name']}")
    
    db.commit()
    return created_tags

def create_test_products(db: Session, categories, tags):
    """建立測試商品"""
    print("🛍️ 建立測試商品...")
    
    products_data = [
        {
            "name": "iPhone 15 Pro 256GB",
            "slug": "iphone-15-pro-256gb",
            "description": "最新 iPhone 15 Pro，搭載 A17 Pro 晶片，支援 USB-C 連接",
            "short_description": "最新 iPhone 15 Pro，強大效能與優雅設計的完美結合",
            "price": 36900.00,
            "sale_price": 34900.00,
            "stock_quantity": 50,
            "sku": "IP15P256",
            "category": "electronics",
            "tags": ["new", "hot", "recommended"],
            "is_featured": True
        },
        {
            "name": "MacBook Air M3 13吋",
            "slug": "macbook-air-m3-13inch",
            "description": "全新 MacBook Air 搭載 M3 晶片，輕薄便攜，效能卓越",
            "short_description": "搭載 M3 晶片的 MacBook Air，專業工作的理想選擇",
            "price": 39900.00,
            "sale_price": None,
            "stock_quantity": 30,
            "sku": "MBA13M3",
            "category": "electronics",
            "tags": ["new", "recommended"],
            "is_featured": True
        },
        {
            "name": "Nike Air Force 1 白色",
            "slug": "nike-air-force-1-white",
            "description": "經典 Nike Air Force 1 白色款，百搭時尚，舒適耐穿",
            "short_description": "經典百搭的 Nike Air Force 1，時尚與舒適的完美平衡",
            "price": 3200.00,
            "sale_price": 2680.00,
            "stock_quantity": 80,
            "sku": "NAF1W",
            "category": "fashion",
            "tags": ["hot", "sale"],
            "is_featured": True
        },
        {
            "name": "Dyson V15 無線吸塵器",
            "slug": "dyson-v15-vacuum",
            "description": "Dyson V15 無線吸塵器，強力吸力，智能感應，深層清潔",
            "short_description": "Dyson V15 無線吸塵器，家庭清潔的智能助手",
            "price": 22900.00,
            "sale_price": None,
            "stock_quantity": 25,
            "sku": "DV15",
            "category": "home",
            "tags": ["recommended", "new"],
            "is_featured": True
        },
        {
            "name": "SK-II 青春露 230ml",
            "slug": "sk2-facial-treatment-essence",
            "description": "SK-II 經典青春露，含有 Pitera™ 成分，改善肌膚質感",
            "short_description": "SK-II 青春露，讓肌膚重現青春光采",
            "price": 8800.00,
            "sale_price": 7920.00,
            "stock_quantity": 40,
            "sku": "SK2FTE230",
            "category": "beauty",
            "tags": ["hot", "sale", "recommended"],
            "is_featured": False
        },
        {
            "name": "Fitbit Charge 6 智慧手環",
            "slug": "fitbit-charge-6",
            "description": "Fitbit Charge 6 智慧手環，全天候健康監測，GPS 定位",
            "short_description": "Fitbit Charge 6，您的健康管理專家",
            "price": 5990.00,
            "sale_price": None,
            "stock_quantity": 60,
            "sku": "FBC6",
            "category": "sports",
            "tags": ["new", "recommended"],
            "is_featured": False
        },
        {
            "name": "Uniqlo Heattech 發熱衣",
            "slug": "uniqlo-heattech-shirt",
            "description": "Uniqlo Heattech 發熱衣，保暖舒適，冬季必備單品",
            "short_description": "Uniqlo Heattech 發熱衣，溫暖過冬的貼心選擇",
            "price": 590.00,
            "sale_price": 490.00,
            "stock_quantity": 200,
            "sku": "UHT001",
            "category": "fashion",
            "tags": ["hot", "sale"],
            "is_featured": False
        },
        {
            "name": "IKEA BILLY 書櫃",
            "slug": "ikea-billy-bookcase",
            "description": "IKEA BILLY 書櫃，簡約設計，可調式層板，收納好幫手",
            "short_description": "IKEA BILLY 書櫃，簡約實用的收納解決方案",
            "price": 1999.00,
            "sale_price": None,
            "stock_quantity": 15,
            "sku": "IKBILLY",
            "category": "home",
            "tags": ["practical"],
            "is_featured": False
        },
        {
            "name": "Sony WH-1000XM5 降噪耳機",
            "slug": "sony-wh1000xm5",
            "description": "Sony WH-1000XM5 無線降噪耳機，業界領先的降噪技術",
            "short_description": "Sony WH-1000XM5，沉浸式音樂體驗",
            "price": 11900.00,
            "sale_price": 10900.00,
            "stock_quantity": 35,
            "sku": "SWH1000XM5",
            "category": "electronics",
            "tags": ["hot", "sale", "recommended"],
            "is_featured": False
        },
        {
            "name": "Adidas Ultraboost 22 跑鞋",
            "slug": "adidas-ultraboost-22",
            "description": "Adidas Ultraboost 22 跑鞋，Boost 中底技術，跑步首選",
            "short_description": "Adidas Ultraboost 22，為跑者而生的專業跑鞋",
            "price": 5490.00,
            "sale_price": None,
            "stock_quantity": 45,
            "sku": "AUB22",
            "category": "sports",
            "tags": ["new", "recommended"],
            "is_featured": False
        }
    ]
    
    created_products = []
    category_map = {cat.slug: cat for cat in categories}
    tag_map = {tag.slug: tag for tag in tags}
    
    for prod_data in products_data:
        existing_product = db.query(Product).filter(Product.slug == prod_data["slug"]).first()
        if existing_product:
            print(f"   商品 {prod_data['name']} 已存在，跳過...")
            created_products.append(existing_product)
            continue
            
        product = Product(
            name=prod_data["name"],
            slug=prod_data["slug"],
            description=prod_data["description"],
            short_description=prod_data["short_description"],
            price=Decimal(str(prod_data["price"])),
            sale_price=Decimal(str(prod_data["sale_price"])) if prod_data["sale_price"] else None,
            stock_quantity=prod_data["stock_quantity"],
            sku=prod_data["sku"],
            is_active=True,
            is_featured=prod_data["is_featured"],
            featured_image=f"/static/images/products/{prod_data['slug']}.jpg",
            meta_title=prod_data["name"],
            meta_description=prod_data["short_description"]
        )
        
        # 關聯分類
        if prod_data["category"] in category_map:
            product.categories.append(category_map[prod_data["category"]])
        
        # 關聯標籤
        for tag_slug in prod_data["tags"]:
            if tag_slug in tag_map:
                product.tags.append(tag_map[tag_slug])
        
        db.add(product)
        created_products.append(product)
        print(f"   ✅ 建立商品: {prod_data['name']} (價格: NT${prod_data['price']})")
    
    db.commit()
    return created_products

def create_test_posts(db: Session, categories, tags):
    """建立測試文章"""
    print("📝 建立測試文章...")
    
    posts_data = [
        {
            "title": "iPhone 15 Pro 完整評測：值得升級嗎？",
            "slug": "iphone-15-pro-review",
            "content": "Apple 最新推出的 iPhone 15 Pro 帶來了許多令人驚艷的新功能...",
            "excerpt": "深度評測 iPhone 15 Pro 的各項功能與效能表現",
            "category": "technology",
            "tags": ["review"],
            "is_published": True
        },
        {
            "title": "2024 冬季保暖單品推薦",
            "slug": "winter-fashion-2024",
            "content": "寒冷的冬天即將到來，如何搭配既時尚又保暖的服飾呢？",
            "excerpt": "精選 2024 年冬季必備保暖單品，讓你溫暖又時尚",
            "category": "lifestyle",
            "tags": ["practical"],
            "is_published": True
        },
        {
            "title": "居家收納神器大盤點",
            "slug": "home-storage-solutions",
            "content": "善用收納工具，讓居家空間更整潔有序，生活品質大提升...",
            "excerpt": "分享實用的居家收納技巧與好用的收納商品推薦",
            "category": "shopping",
            "tags": ["practical", "tutorial"],
            "is_published": True
        }
    ]
    
    created_posts = []
    category_map = {cat.slug: cat for cat in categories}
    tag_map = {tag.slug: tag for tag in tags}
    
    for post_data in posts_data:
        existing_post = db.query(Post).filter(Post.slug == post_data["slug"]).first()
        if existing_post:
            print(f"   文章 {post_data['title']} 已存在，跳過...")
            created_posts.append(existing_post)
            continue
            
        post = Post(
            title=post_data["title"],
            slug=post_data["slug"],
            content=post_data["content"] + "\n\n" + "這是一篇測試文章，內容僅供演示使用。" * 10,
            excerpt=post_data["excerpt"],
            is_published=post_data["is_published"],
            featured_image=f"/static/images/posts/{post_data['slug']}.jpg",
            meta_title=post_data["title"],
            meta_description=post_data["excerpt"]
        )
        
        # 關聯分類
        if post_data["category"] in category_map:
            post.categories.append(category_map[post_data["category"]])
        
        # 關聯標籤
        for tag_slug in post_data["tags"]:
            if tag_slug in tag_map:
                post.tags.append(tag_map[tag_slug])
        
        db.add(post)
        created_posts.append(post)
        print(f"   ✅ 建立文章: {post_data['title']}")
    
    db.commit()
    return created_posts

def create_test_orders(db: Session, users, products):
    """建立測試訂單"""
    print("📦 建立測試訂單...")
    
    # 排除管理員用戶
    regular_users = [user for user in users if user.role == UserRole.USER]
    
    if not regular_users or not products:
        print("   ⚠️ 沒有足夠的用戶或商品來建立訂單")
        return []
    
    created_orders = []
    order_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    
    # 為每個用戶建立 1-3 個訂單
    for user in regular_users:
        num_orders = random.randint(1, 3)
        
        for i in range(num_orders):
            # 隨機選擇 1-4 個商品
            selected_products = random.sample(products, random.randint(1, min(4, len(products))))
            
            # 生成訂單編號
            order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            
            order = Order(
                order_number=order_number,
                customer_name=user.full_name,
                customer_email=user.email,
                customer_phone=f"09{random.randint(10000000, 99999999)}",
                shipping_address=f"台北市{random.choice(['中山區', '信義區', '大安區', '松山區', '內湖區'])}測試街道{random.randint(1, 100)}號",
                status=random.choice(order_statuses),
                user_id=user.id,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            
            total_amount = Decimal('0')
            
            # 建立訂單項目
            for product in selected_products:
                quantity = random.randint(1, 3)
                price = product.sale_price if product.sale_price else product.price
                item_total = price * quantity
                total_amount += item_total
                
                order_item = OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    product_price=price,
                    quantity=quantity
                )
                order.items.append(order_item)
            
            order.subtotal = total_amount
            order.shipping_fee = Decimal('60')  # 預設運費
            order.total_amount = total_amount + order.shipping_fee
            
            db.add(order)
            created_orders.append(order)
            
            print(f"   ✅ 建立訂單: {user.full_name} - NT${total_amount} ({order.status})")
    
    db.commit()
    return created_orders

def main():
    """主函數"""
    print("🚀 開始建立測試資料...")
    print("=" * 50)
    
    # 初始化資料庫
    init_db()
    
    # 獲取資料庫連接
    db = next(get_db())
    
    try:
        # 建立測試資料
        users = create_test_users(db)
        categories = create_test_categories(db)
        tags = create_test_tags(db)
        products = create_test_products(db, categories, tags)
        posts = create_test_posts(db, categories, tags)
        orders = create_test_orders(db, users, products)
        
        print("=" * 50)
        print("✅ 測試資料建立完成！")
        print()
        print("📊 建立統計:")
        print(f"   👥 用戶: {len(users)} 個")
        print(f"   📁 分類: {len(categories)} 個")
        print(f"   🏷️ 標籤: {len(tags)} 個")
        print(f"   🛍️ 商品: {len(products)} 個")
        print(f"   📝 文章: {len(posts)} 篇")
        print(f"   📦 訂單: {len(orders)} 個")
        print()
        print("🔑 測試帳號:")
        print("   管理員:")
        print("     帳號: admin")
        print("     密碼: admin123456")
        print()
        print("   一般用戶:")
        test_accounts = [
            ("user001", "password123", "張小明"),
            ("user002", "password123", "李小華"),
            ("demo", "demo123", "演示帳號"),
            ("test", "test123", "測試帳號")
        ]
        for username, password, fullname in test_accounts:
            print(f"     帳號: {username} | 密碼: {password} | 姓名: {fullname}")
        print()
        print("🌐 訪問網址:")
        print("   前台: http://localhost:8000")
        print("   管理後台: http://localhost:8000/admin/login")
        
    except Exception as e:
        print(f"❌ 建立測試資料時發生錯誤: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 