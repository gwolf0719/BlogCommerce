#!/usr/bin/env python3
"""
資料庫初始化腳本
建立資料表並插入初始資料
"""

from database import create_tables, get_db
from models.models import User, Category, Tag
from api.auth import get_password_hash
from sqlalchemy.orm import Session

def init_database():
    """初始化資料庫"""
    print("🚀 正在初始化資料庫...")
    
    # 建立資料表
    create_tables()
    print("✅ 資料表已建立")
    
    # 取得資料庫會話
    db = next(get_db())
    
    try:
        # 建立預設管理員帳號
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_password = get_password_hash("admin123")
            admin_user = User(
                username="admin",
                email="admin@blogcommerce.local",
                hashed_password=admin_password,
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
            print("✅ 已建立預設管理員帳號")
            print("   帳號: admin")
            print("   密碼: admin123")
            print("   請於正式環境中變更預設密碼！")
        else:
            print("ℹ️  管理員帳號已存在")
        
        # 建立預設分類
        default_categories = [
            {"name": "科技", "slug": "technology", "description": "科技相關文章和產品"},
            {"name": "生活", "slug": "lifestyle", "description": "生活相關文章和產品"},
            {"name": "設計", "slug": "design", "description": "設計相關文章和產品"},
        ]
        
        for cat_data in default_categories:
            existing_cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not existing_cat:
                category = Category(**cat_data)
                db.add(category)
        
        print("✅ 已建立預設分類")
        
        # 建立預設標籤
        default_tags = [
            {"name": "新聞", "slug": "news"},
            {"name": "教學", "slug": "tutorial"},
            {"name": "評測", "slug": "review"},
            {"name": "趨勢", "slug": "trends"},
        ]
        
        for tag_data in default_tags:
            existing_tag = db.query(Tag).filter(Tag.slug == tag_data["slug"]).first()
            if not existing_tag:
                tag = Tag(**tag_data)
                db.add(tag)
        
        print("✅ 已建立預設標籤")
        
        # 提交變更
        db.commit()
        print("🎉 資料庫初始化完成！")
        
    except Exception as e:
        print(f"❌ 初始化過程中發生錯誤: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_sample_data():
    """建立範例資料 (可選)"""
    print("📝 正在建立範例資料...")
    
    db = next(get_db())
    
    try:
        from models.models import Post, Product
        from datetime import datetime
        
        # 取得管理員使用者和分類
        admin_user = db.query(User).filter(User.username == "admin").first()
        tech_category = db.query(Category).filter(Category.slug == "technology").first()
        lifestyle_category = db.query(Category).filter(Category.slug == "lifestyle").first()
        
        if admin_user and tech_category:
            # 建立範例文章
            sample_posts = [
                {
                    "title": "歡迎使用 BlogCommerce 系統",
                    "slug": "welcome-to-blogcommerce",
                    "content": "這是一篇範例文章，展示 BlogCommerce 系統的部落格功能。您可以在管理後台編輯或刪除此文章。",
                    "excerpt": "歡迎使用 BlogCommerce 系統的範例文章",
                    "is_published": True,
                    "published_at": datetime.utcnow(),
                    "author_id": admin_user.id,
                    "category_id": tech_category.id,
                    "meta_title": "歡迎使用 BlogCommerce",
                    "meta_description": "BlogCommerce 部落格電商系統的歡迎文章"
                },
                {
                    "title": "如何使用管理後台",
                    "slug": "how-to-use-admin-panel",
                    "content": "這篇文章將教您如何使用 BlogCommerce 的管理後台功能，包括文章管理、商品管理和訂單管理。",
                    "excerpt": "管理後台使用教學",
                    "is_published": True,
                    "published_at": datetime.utcnow(),
                    "author_id": admin_user.id,
                    "category_id": tech_category.id,
                    "meta_title": "管理後台使用教學",
                    "meta_description": "學習如何使用 BlogCommerce 管理後台"
                }
            ]
            
            for post_data in sample_posts:
                existing_post = db.query(Post).filter(Post.slug == post_data["slug"]).first()
                if not existing_post:
                    post = Post(**post_data)
                    db.add(post)
            
            print("✅ 已建立範例文章")
        
        # 建立範例商品
        if tech_category and lifestyle_category:
            sample_products = [
                {
                    "name": "範例商品 - 科技產品",
                    "slug": "sample-tech-product",
                    "description": "這是一個範例科技商品，展示商品管理功能。",
                    "short_description": "範例科技商品",
                    "price": 999.0,
                    "sale_price": 799.0,
                    "sku": "TECH-001",
                    "stock_quantity": 50,
                    "is_active": True,
                    "is_featured": True,
                    "category_id": tech_category.id,
                    "meta_title": "範例科技商品",
                    "meta_description": "這是一個展示用的範例科技商品"
                },
                {
                    "name": "範例商品 - 生活用品",
                    "slug": "sample-lifestyle-product",
                    "description": "這是一個範例生活商品，展示多分類商品管理。",
                    "short_description": "範例生活商品",
                    "price": 299.0,
                    "sku": "LIFE-001",
                    "stock_quantity": 100,
                    "is_active": True,
                    "category_id": lifestyle_category.id,
                    "meta_title": "範例生活商品",
                    "meta_description": "這是一個展示用的範例生活商品"
                }
            ]
            
            for product_data in sample_products:
                existing_product = db.query(Product).filter(Product.slug == product_data["slug"]).first()
                if not existing_product:
                    product = Product(**product_data)
                    db.add(product)
            
            print("✅ 已建立範例商品")
        
        db.commit()
        print("🎉 範例資料建立完成！")
        
    except Exception as e:
        print(f"❌ 建立範例資料時發生錯誤: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--with-sample":
        init_database()
        create_sample_data()
    else:
        init_database()
        print("\n💡 提示：使用 'python init_db.py --with-sample' 來同時建立範例資料") 