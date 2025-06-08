#!/usr/bin/env python3
"""
初始化系統設定
"""
from app.database import SessionLocal
from app.models.settings import SystemSettings

def init_default_settings():
    """初始化預設系統設定"""
    db = SessionLocal()
    
    try:
        # 功能開關設定
        feature_settings = [
            {
                "key": "blog_enabled",
                "value": "true",
                "description": "啟用部落格功能",
                "category": "features",
                "data_type": "boolean",
                "is_public": True
            },
            {
                "key": "shop_enabled",
                "value": "true",
                "description": "啟用商店功能",
                "category": "features",
                "data_type": "boolean",
                "is_public": True
            },
            {
                "key": "comment_enabled",
                "value": "true",
                "description": "啟用評論功能",
                "category": "features",
                "data_type": "boolean",
                "is_public": True
            },
            {
                "key": "analytics_enabled",
                "value": "true",
                "description": "啟用流量分析功能",
                "category": "features",
                "data_type": "boolean",
                "is_public": True
            },
            {
                "key": "search_enabled",
                "value": "true",
                "description": "啟用搜尋功能",
                "category": "features",
                "data_type": "boolean",
                "is_public": True
            },
            {
                "key": "newsletter_enabled",
                "value": "false",
                "description": "啟用電子報功能",
                "category": "features",
                "data_type": "boolean",
                "is_public": True
            }
        ]
        
        # 基本設定
        general_settings = [
            {
                "key": "site_name",
                "value": "BlogCommerce",
                "description": "網站名稱",
                "category": "general",
                "data_type": "string",
                "is_public": True
            },
            {
                "key": "site_description",
                "value": "部落格與電商整合平台",
                "description": "網站描述",
                "category": "general",
                "data_type": "string",
                "is_public": True
            },
            {
                "key": "site_keywords",
                "value": "電商,部落格,購物",
                "description": "網站關鍵字",
                "category": "general",
                "data_type": "string",
                "is_public": True
            },
            {
                "key": "maintenance_mode",
                "value": "false",
                "description": "維護模式",
                "category": "general",
                "data_type": "boolean",
                "is_public": True
            },
            {
                "key": "registration_enabled",
                "value": "true",
                "description": "允許會員註冊",
                "category": "general",
                "data_type": "boolean",
                "is_public": True
            }
        ]
        
        # SEO 設定
        seo_settings = [
            {
                "key": "meta_title",
                "value": "BlogCommerce - 部落格與電商整合平台",
                "description": "預設 Meta Title",
                "category": "seo",
                "data_type": "string",
                "is_public": True
            },
            {
                "key": "meta_description",
                "value": "結合部落格與電商功能的現代化平台，提供優質的購物和閱讀體驗",
                "description": "預設 Meta Description",
                "category": "seo",
                "data_type": "string",
                "is_public": True
            },
            {
                "key": "meta_keywords",
                "value": "電商,部落格,購物,文章,商品",
                "description": "預設 Meta Keywords",
                "category": "seo",
                "data_type": "string",
                "is_public": True
            },
            {
                "key": "google_analytics_id",
                "value": "",
                "description": "Google Analytics ID",
                "category": "seo",
                "data_type": "string",
                "is_public": False
            },
            {
                "key": "google_tag_manager_id",
                "value": "",
                "description": "Google Tag Manager ID",
                "category": "seo",
                "data_type": "string",
                "is_public": False
            }
        ]
        
        # 電商設定
        ecommerce_settings = [
            {
                "key": "currency",
                "value": "TWD",
                "description": "預設貨幣",
                "category": "ecommerce",
                "data_type": "string",
                "is_public": True
            },
            {
                "key": "currency_symbol",
                "value": "NT$",
                "description": "貨幣符號",
                "category": "ecommerce",
                "data_type": "string",
                "is_public": True
            },
            {
                "key": "free_shipping_threshold",
                "value": "1000",
                "description": "免運費門檻",
                "category": "ecommerce",
                "data_type": "float",
                "is_public": True
            },
            {
                "key": "default_shipping_fee",
                "value": "60",
                "description": "預設運費",
                "category": "ecommerce",
                "data_type": "float",
                "is_public": True
            },
            {
                "key": "tax_rate",
                "value": "0.05",
                "description": "稅率",
                "category": "ecommerce",
                "data_type": "float",
                "is_public": True
            }
        ]
        
        # 合併所有設定
        all_settings = feature_settings + general_settings + seo_settings + ecommerce_settings
        
        # 檢查並創建設定
        for setting_data in all_settings:
            existing = db.query(SystemSettings).filter(
                SystemSettings.key == setting_data["key"]
            ).first()
            
            if not existing:
                setting = SystemSettings(**setting_data)
                db.add(setting)
                print(f"創建設定: {setting_data['key']} = {setting_data['value']}")
            else:
                print(f"設定已存在: {setting_data['key']}")
        
        db.commit()
        print("設定初始化完成！")
        
    except Exception as e:
        print(f"初始化設定時發生錯誤: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("開始初始化系統設定...")
    init_default_settings() 