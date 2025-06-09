#!/usr/bin/env python3
"""
啟用AI功能腳本
"""

import sys
import os

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models.settings import SystemSettings
from sqlalchemy.orm import sessionmaker

def enable_ai():
    """啟用AI功能"""
    print("🔧 正在啟用AI功能...")
    
    # 創建資料庫會話
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 啟用AI功能
        ai_enabled = db.query(SystemSettings).filter(SystemSettings.key == 'ai_enabled').first()
        if ai_enabled:
            ai_enabled.value = 'true'
            print("✅ AI功能已啟用")
        
        # 啟用圖片生成
        ai_image_enabled = db.query(SystemSettings).filter(SystemSettings.key == 'ai_image_enabled').first()
        if ai_image_enabled:
            ai_image_enabled.value = 'true'
            print("✅ AI圖片生成已啟用")
        
        # 設定測試API密鑰（請替換為真實的API密鑰）
        test_api_key = input("請輸入您的OpenAI API密鑰（或按Enter跳過）: ").strip()
        if test_api_key:
            ai_api_key = db.query(SystemSettings).filter(SystemSettings.key == 'ai_api_key').first()
            if ai_api_key:
                ai_api_key.value = test_api_key
                print("✅ API密鑰已設定")
        
        # 提交更改
        db.commit()
        print("✅ 設定已保存")
        
    except Exception as e:
        print(f"❌ 啟用AI功能時發生錯誤: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 AI功能啟用工具")
    print("=" * 50)
    
    enable_ai()
    
    print("=" * 50)
    print("🎉 完成！現在可以使用AI功能了")
    print("\n📝 提示:")
    print("1. 確保您有有效的OpenAI API密鑰")
    print("2. 在後台管理的系統設定中可以調整AI參數")
    print("3. 在文章編輯頁面中可以使用AI生成功能") 