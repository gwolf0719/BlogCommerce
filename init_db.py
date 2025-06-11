#!/usr/bin/env python3
"""
資料庫初始化腳本
建立範例文章和商品
"""
from app.database import SessionLocal, init_db
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
        # 分類和標籤已移除
        
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