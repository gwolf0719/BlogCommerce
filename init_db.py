#!/usr/bin/env python3
"""
資料庫初始化腳本
建立範例分類、標籤、文章和商品
"""
from app.database import SessionLocal, init_db
from app.models.category import Category, CategoryType
from app.models.tag import Tag, TagType
from app.models.post import Post
from app.models.product import Product
from app.models.user import User, UserRole
from app.auth import get_password_hash
from app.config import settings
from decimal import Decimal


def create_sample_data():
    """建立範例資料"""
    db = SessionLocal()
    
    try:
        # 檢查是否已有管理員帳號
        admin_user = db.query(User).filter(User.email == settings.admin_email).first()
        if not admin_user:
            # 建立管理員帳號
            admin_user = User(
                username=settings.admin_username,
                email=settings.admin_email,
                full_name=settings.admin_full_name,
                hashed_password=get_password_hash(settings.admin_password),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            print(f"✅ 建立管理員帳號: {settings.admin_email}")
        else:
            print(f"ℹ️  管理員帳號已存在: {settings.admin_email}")
        # 建立部落格分類
        blog_categories = [
            Category(name="技術文章", description="程式設計與技術相關文章", type=CategoryType.BLOG, slug="tech"),
            Category(name="生活分享", description="日常生活與心得分享", type=CategoryType.BLOG, slug="life"),
            Category(name="產品評測", description="各種產品的使用心得", type=CategoryType.BLOG, slug="review"),
        ]
        
        # 建立商品分類
        product_categories = [
            Category(name="電子產品", description="各種電子設備與配件", type=CategoryType.PRODUCT, slug="electronics"),
            Category(name="服飾配件", description="衣服、鞋子與配件", type=CategoryType.PRODUCT, slug="fashion"),
            Category(name="書籍文具", description="書籍、筆記本與文具用品", type=CategoryType.PRODUCT, slug="books"),
        ]
        
        db.add_all(blog_categories + product_categories)
        db.flush()
        
        # 建立部落格標籤
        blog_tags = [
            Tag(name="Python", description="Python 程式語言", type=TagType.BLOG, slug="python"),
            Tag(name="Web開發", description="網頁開發相關", type=TagType.BLOG, slug="web-dev"),
            Tag(name="教學", description="教學文章", type=TagType.BLOG, slug="tutorial"),
            Tag(name="心得", description="個人心得分享", type=TagType.BLOG, slug="experience"),
        ]
        
        # 建立商品標籤
        product_tags = [
            Tag(name="熱銷", description="熱銷商品", type=TagType.PRODUCT, slug="bestseller"),
            Tag(name="新品", description="最新商品", type=TagType.PRODUCT, slug="new"),
            Tag(name="推薦", description="推薦商品", type=TagType.PRODUCT, slug="recommended"),
            Tag(name="限時特價", description="限時優惠商品", type=TagType.PRODUCT, slug="sale"),
        ]
        
        db.add_all(blog_tags + product_tags)
        db.flush()
        
        # 建立範例文章
        posts = [
            Post(
                title="FastAPI 快速入門指南",
                content="這是一篇關於 FastAPI 的詳細教學文章...",
                excerpt="學習如何使用 FastAPI 建立現代化的 Web API",
                is_published=True,
                slug="fastapi-tutorial",
                meta_title="FastAPI 教學 - 現代化 Python Web 框架",
                meta_description="完整的 FastAPI 教學指南，從基礎到進階應用"
            ),
            Post(
                title="Python 資料結構與演算法",
                content="深入探討 Python 中的各種資料結構...",
                excerpt="掌握 Python 程式設計的核心概念",
                is_published=True,
                slug="python-data-structures",
                meta_title="Python 資料結構完整指南",
                meta_description="學習 Python 資料結構與演算法的最佳實踐"
            ),
        ]
        
        db.add_all(posts)
        db.flush()
        
        # 為文章設定分類和標籤
        posts[0].categories = [blog_categories[0]]  # 技術文章
        posts[0].tags = [blog_tags[0], blog_tags[1], blog_tags[2]]  # Python, Web開發, 教學
        
        posts[1].categories = [blog_categories[0]]  # 技術文章
        posts[1].tags = [blog_tags[0], blog_tags[2]]  # Python, 教學
        
        # 建立範例商品
        products = [
            Product(
                name="無線藍牙耳機",
                description="高品質無線藍牙耳機，支援主動降噪功能，電池續航力長達 30 小時。",
                short_description="高品質無線藍牙耳機",
                price=Decimal("2999.00"),
                sale_price=Decimal("2599.00"),
                stock_quantity=50,
                sku="BT-HEADPHONE-001",
                is_active=True,
                is_featured=True,
                slug="bluetooth-headphones",
                meta_title="無線藍牙耳機 - 高品質音響體驗",
                meta_description="專業級無線藍牙耳機，主動降噪，長續航力"
            ),
            Product(
                name="程式設計筆記本",
                description="專為程式設計師設計的筆記本，包含常用語法參考和空白頁面。",
                short_description="程式設計師專用筆記本",
                price=Decimal("299.00"),
                stock_quantity=100,
                sku="NOTEBOOK-PROG-001",
                is_active=True,
                slug="programming-notebook",
                meta_title="程式設計筆記本 - 開發者必備",
                meta_description="專為程式設計師設計的筆記本，提升開發效率"
            ),
        ]
        
        db.add_all(products)
        db.flush()
        
        # 為商品設定分類和標籤
        products[0].categories = [product_categories[0]]  # 電子產品
        products[0].tags = [product_tags[0], product_tags[2], product_tags[3]]  # 熱銷, 推薦, 限時特價
        
        products[1].categories = [product_categories[2]]  # 書籍文具
        products[1].tags = [product_tags[1], product_tags[2]]  # 新品, 推薦
        
        db.commit()
        print("✅ 範例資料建立完成！")
        
        # 顯示管理員帳號資訊
        print("=" * 60)
        print("🔑 管理員帳號資訊:")
        print(f"   使用者名稱: {settings.admin_username}")
        print(f"   電子郵件: {settings.admin_email}")
        print(f"   密碼: {settings.admin_password}")
        print(f"   管理後台網址: {settings.site_url}/admin")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 建立範例資料時發生錯誤: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """主要執行函數"""
    print("🔄 初始化資料庫...")
    init_db()
    print("✅ 資料庫初始化完成！")
    
    print("🔄 建立範例資料...")
    create_sample_data()
    
    print("🎉 所有設定完成！")
    print("📖 您可以使用以下指令啟動伺服器:")
    print("   python run.py")
    print("🌐 然後開啟瀏覽器前往: http://127.0.0.1:8000")
    print("📚 API 文件: http://127.0.0.1:8000/docs")


if __name__ == "__main__":
    main() 