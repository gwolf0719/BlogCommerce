import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 網站基本資訊
    site_name: str = "BlogCommerce"
    site_description: str = "部落格與電商整合平台"
    site_url: str = "http://localhost:8001"
    site_logo: str = "/static/images/logo.png"
    site_favicon: str = "/static/images/favicon.ico"
    
    # 應用程式設定
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    
    # 資料庫設定
    database_url: str = "sqlite:///./blogcommerce.db"
    
    # JWT 設定
    jwt_secret_key: str = "jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # 管理員帳號設定
    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123456"
    admin_full_name: str = "系統管理員"
    
    # 郵件設定
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_from_name: str = "BlogCommerce"
    
    # 檔案上傳設定
    upload_folder: str = "app/static/uploads"
    max_file_size: int = 5242880  # 5MB
    allowed_extensions: str = "jpg,jpeg,png,gif,webp,pdf,doc,docx"
    
    # 分頁設定
    posts_per_page: int = 10
    products_per_page: int = 20
    orders_per_page: int = 20
    
    # 電商設定
    default_currency: str = "TWD"
    default_currency_symbol: str = "NT$"
    free_shipping_threshold: float = 1000.0
    default_shipping_fee: float = 60.0
    tax_rate: float = 0.05
    
    # 社群媒體連結
    facebook_url: str = ""
    instagram_url: str = ""
    twitter_url: str = ""
    youtube_url: str = ""
    
    # SEO 設定
    default_meta_title: str = "BlogCommerce - 部落格與電商整合平台"
    default_meta_description: str = "結合部落格與電商功能的現代化平台，提供優質的購物和閱讀體驗"
    default_meta_keywords: str = "電商,部落格,購物,文章,商品"
    
    # Google Analytics
    google_analytics_id: str = ""
    google_tag_manager_id: str = ""
    
    # 第三方服務
    recaptcha_site_key: str = ""
    recaptcha_secret_key: str = ""
    
    # 快取設定
    redis_url: str = "redis://localhost:6379/0"
    cache_type: str = "simple"
    cache_default_timeout: int = 300
    
    # 備份設定
    backup_enabled: bool = False
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 30
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


settings = Settings() 