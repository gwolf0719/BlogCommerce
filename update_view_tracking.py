#!/usr/bin/env python3
"""
資料庫更新腳本：添加瀏覽追蹤功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings
from app.database import Base, SessionLocal
from app.models import *  # 匯入所有模型
from app.utils.logger import app_logger

def update_database():
    """更新資料庫結構"""
    try:
        # 創建資料庫引擎
        engine = create_engine(settings.database_url)
        
        # 創建所有表格（如果不存在）
        Base.metadata.create_all(bind=engine)
        
        # 檢查並更新 posts 表格
        with engine.connect() as conn:
            # 檢查 posts 表是否有 view_count 欄位
            try:
                result = conn.execute(text("SELECT view_count FROM posts LIMIT 1"))
                app_logger.info("Posts 表的 view_count 欄位已存在")
            except Exception:
                # 添加 view_count 欄位到 posts 表
                conn.execute(text("ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0 NOT NULL"))
                app_logger.info("已添加 view_count 欄位到 posts 表")
            
            # 檢查 products 表是否有 view_count 欄位
            try:
                result = conn.execute(text("SELECT view_count FROM products LIMIT 1"))
                app_logger.info("Products 表的 view_count 欄位已存在")
            except Exception:
                # 添加 view_count 欄位到 products 表
                conn.execute(text("ALTER TABLE products ADD COLUMN view_count INTEGER DEFAULT 0 NOT NULL"))
                app_logger.info("已添加 view_count 欄位到 products 表")
            
            # 檢查 view_logs 表是否存在
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM view_logs LIMIT 1"))
                app_logger.info("View_logs 表已存在")
            except Exception:
                app_logger.info("View_logs 表將由 SQLAlchemy 自動創建")
            
            conn.commit()
        
        app_logger.info("資料庫更新完成！")
        
    except Exception as e:
        app_logger.error(f"資料庫更新失敗: {e}")
        raise

def init_view_counts():
    """初始化現有文章和商品的瀏覽計數"""
    try:
        db = SessionLocal()
        
        # 更新所有文章的 view_count 為 0（如果為 NULL）
        db.execute(text("UPDATE posts SET view_count = 0 WHERE view_count IS NULL"))
        
        # 更新所有商品的 view_count 為 0（如果為 NULL）
        db.execute(text("UPDATE products SET view_count = 0 WHERE view_count IS NULL"))
        
        db.commit()
        db.close()
        
        app_logger.info("瀏覽計數初始化完成！")
        
    except Exception as e:
        app_logger.error(f"瀏覽計數初始化失敗: {e}")
        raise

if __name__ == "__main__":
    print("正在更新資料庫結構...")
    update_database()
    
    print("正在初始化瀏覽計數...")
    init_view_counts()
    
    print("瀏覽追蹤功能已成功添加到系統中！")
    print("\n新功能包括：")
    print("1. 文章和商品的瀏覽計數")
    print("2. 詳細的瀏覽記錄（包含用戶、IP、時間等）")
    print("3. 瀏覽統計 API 端點")
    print("4. 熱門內容查詢")
    print("5. 用戶瀏覽歷史") 