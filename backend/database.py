from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # 資料庫配置
    database_url: str = "sqlite:///./blog_shop.db"
    database_type: str = "sqlite"  # sqlite, mysql, postgresql
    
    # JWT 配置
    jwt_secret: str = "your_super_secret_jwt_key_here_change_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 應用配置
    app_name: str = "BlogCommerce"
    app_version: str = "1.0.0"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    
    # CORS 配置
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # 檔案上傳配置
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    
    # 分頁配置
    default_page_size: int = 20
    max_page_size: int = 100
    
    # 電商配置
    default_currency: str = "TWD"
    shipping_cost: float = 100.0
    free_shipping_threshold: float = 1000.0
    
    # SEO 配置
    site_name: str = "BlogCommerce"
    site_description: str = "一個現代化的部落格電商系統"
    site_url: str = "http://localhost:3000"
    
    # 郵件配置 (可選)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = ""
    
    class Config:
        env_file = "../.env"
        case_sensitive = False

settings = Settings()

def get_database_engine():
    """根據資料庫類型建立對應的引擎"""
    connect_args = {}
    
    if settings.database_type.lower() == "sqlite":
        # SQLite 特定設定
        connect_args = {"check_same_thread": False}
        
    elif settings.database_type.lower() == "mysql":
        # MySQL 特定設定
        connect_args = {
            "charset": "utf8mb4",
            "autocommit": True
        }
        
    elif settings.database_type.lower() == "postgresql":
        # PostgreSQL 特定設定
        connect_args = {}
    
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=settings.debug  # 在debug模式下顯示SQL
    )
    
    return engine

# 建立引擎
engine = get_database_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 資料庫依賴
def get_db():
    """取得資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """建立所有資料表"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """刪除所有資料表 (僅限開發環境)"""
    if settings.debug:
        Base.metadata.drop_all(bind=engine)
    else:
        raise Exception("不允許在生產環境中刪除資料表") 