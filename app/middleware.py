from fastapi import Request
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models.settings import SystemSettings


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


def get_public_settings() -> dict:
    """獲取所有公開設定"""
    db = SessionLocal()
    try:
        settings = db.query(SystemSettings).filter(
            SystemSettings.is_public == True
        ).all()
        
        settings_dict = {}
        for setting in settings:
            settings_dict[setting.key] = setting.parse_value()
                
        return settings_dict
        
    except Exception as e:
        print(f"獲取公開設定時發生錯誤: {e}")
        return {}
    finally:
        db.close() 