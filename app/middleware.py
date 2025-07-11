from fastapi import Request
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models.settings import SystemSettings
from .config import settings as config_settings


def get_public_settings() -> dict:
    """獲取所有公開設定，包括基本設定和功能設定"""
    db = SessionLocal()
    try:
        settings = db.query(SystemSettings).filter(
            SystemSettings.is_public == True
        ).all()
        
        settings_dict = {}
        for setting in settings:
            settings_dict[setting.key] = setting.parse_value()
        
        # 設定預設值（從配置文件中取得）
        defaults = {
            # 基本設定
            "site_name": config_settings.site_name,
            "site_description": config_settings.site_description,
            "site_url": config_settings.site_url,
            "site_logo": config_settings.site_logo,
            "site_favicon": config_settings.site_favicon,
            "default_currency": config_settings.default_currency,
            "default_currency_symbol": config_settings.default_currency_symbol,
            
            # 功能設定
            "blog_enabled": True,
            "shop_enabled": True,
            "comment_enabled": True,
            "analytics_enabled": True,
            "search_enabled": True,
            "newsletter_enabled": False,
            "user_registration": True,
            "maintenance_mode": False,
            
            # SEO 設定
            "default_meta_title": config_settings.default_meta_title,
            "default_meta_description": config_settings.default_meta_description,
            "default_meta_keywords": config_settings.default_meta_keywords,
            "google_analytics_id": config_settings.google_analytics_id,
            "google_tag_manager_id": config_settings.google_tag_manager_id,
        }
        
        # 合併預設值和資料庫設定（資料庫設定優先）
        for key, default_value in defaults.items():
            if key not in settings_dict:
                settings_dict[key] = default_value
        
        return settings_dict
        
    except Exception as e:
        print(f"獲取公開設定時發生錯誤: {e}")
        # 返回配置文件中的預設值
        return {
            "site_name": config_settings.site_name,
            "site_description": config_settings.site_description,
            "site_url": config_settings.site_url,
            "site_logo": config_settings.site_logo,
            "site_favicon": config_settings.site_favicon,
            "default_currency": config_settings.default_currency,
            "default_currency_symbol": config_settings.default_currency_symbol,
            "blog_enabled": True,
            "shop_enabled": True,
            "comment_enabled": True,
            "analytics_enabled": True,
            "search_enabled": True,
            "newsletter_enabled": False,
            "user_registration": True,
            "maintenance_mode": False,
            "default_meta_title": config_settings.default_meta_title,
            "default_meta_description": config_settings.default_meta_description,
            "default_meta_keywords": config_settings.default_meta_keywords,
            "google_analytics_id": config_settings.google_analytics_id,
            "google_tag_manager_id": config_settings.google_tag_manager_id,
        }
    finally:
        db.close()


def get_feature_settings() -> dict:
    """獲取功能設定"""
    db = SessionLocal()
    try:
        settings = db.query(SystemSettings).filter(
            SystemSettings.category == "features",
            SystemSettings.is_public == True
        ).all()
        
        feature_dict = {}
        for setting in settings:
            feature_dict[setting.key] = setting.parse_value()
        
        # 設定預設值
        defaults = {
            "blog_enabled": True,
            "shop_enabled": True,
            "comment_enabled": True,
            "analytics_enabled": True,
            "search_enabled": True,
            "newsletter_enabled": False
        }
        
        for key, default_value in defaults.items():
            if key not in feature_dict:
                feature_dict[key] = default_value
                
        return feature_dict
        
    except Exception as e:
        print(f"獲取功能設定時發生錯誤: {e}")
        # 返回預設值
        return {
            "blog_enabled": True,
            "shop_enabled": True,
            "comment_enabled": True,
            "analytics_enabled": True,
            "search_enabled": True,
            "newsletter_enabled": False
        }
    finally:
        db.close()