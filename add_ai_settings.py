#!/usr/bin/env python3
"""
添加AI生成文章相關的系統設定
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.settings import SystemSettings

def add_ai_settings():
    """添加AI相關的系統設定"""
    db = next(get_db())
    
    try:
        print("🔄 正在添加AI設定...")
        
        # AI設定列表
        ai_settings = [
            {
                "key": "ai_enabled",
                "value": "false",
                "description": "啟用AI文章生成功能",
                "category": "ai",
                "data_type": "boolean",
                "is_public": False
            },
            {
                "key": "ai_api_provider",
                "value": "openai",
                "description": "AI服務提供商",
                "category": "ai",
                "data_type": "string",
                "is_public": False
            },
            {
                "key": "ai_api_key",
                "value": "",
                "description": "AI API金鑰",
                "category": "ai",
                "data_type": "string",
                "is_public": False
            },
            {
                "key": "ai_api_url",
                "value": "https://api.openai.com/v1",
                "description": "AI API基礎URL",
                "category": "ai",
                "data_type": "string",
                "is_public": False
            },
            {
                "key": "ai_text_model",
                "value": "gpt-3.5-turbo",
                "description": "文字生成模型",
                "category": "ai",
                "data_type": "string",
                "is_public": False
            },
            {
                "key": "ai_image_enabled",
                "value": "false",
                "description": "啟用AI圖片生成",
                "category": "ai",
                "data_type": "boolean",
                "is_public": False
            },
            {
                "key": "ai_image_model",
                "value": "dall-e-3",
                "description": "圖片生成模型",
                "category": "ai",
                "data_type": "string",
                "is_public": False
            },
            {
                "key": "ai_global_prompt",
                "value": "你是一個專業的部落格文章寫手，請根據用戶提供的主題和要求，撰寫高質量的中文部落格文章。文章應該結構清晰、內容豐富、語言流暢，並符合SEO最佳實踐。",
                "description": "全站AI生成風格提示詞",
                "category": "ai",
                "data_type": "string",
                "is_public": False
            },
            {
                "key": "ai_max_tokens",
                "value": "2000",
                "description": "AI生成最大token數",
                "category": "ai",
                "data_type": "integer",
                "is_public": False
            },
            {
                "key": "ai_temperature",
                "value": "0.7",
                "description": "AI生成創意度(0-1)",
                "category": "ai",
                "data_type": "float",
                "is_public": False
            }
        ]
        
        # 檢查並添加設定
        for setting_data in ai_settings:
            existing = db.query(SystemSettings).filter(
                SystemSettings.key == setting_data["key"]
            ).first()
            
            if not existing:
                setting = SystemSettings(**setting_data)
                db.add(setting)
                print(f"✅ 添加設定: {setting_data['key']}")
            else:
                print(f"⚠️  設定已存在: {setting_data['key']}")
        
        db.commit()
        print("✅ AI設定添加完成！")
        
    except Exception as e:
        print(f"❌ 添加AI設定失敗: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_ai_settings() 