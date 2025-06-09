#!/usr/bin/env python3
"""
除錯登入問題
"""

import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User


def debug_login():
    """除錯登入問題"""
    print("🔍 除錯登入問題...")
    
    db = SessionLocal()
    try:
        # 查詢管理員用戶
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("❌ 找不到用戶名為 'admin' 的用戶")
            
            # 列出所有用戶
            all_users = db.query(User).all()
            print(f"📋 資料庫中的所有用戶 ({len(all_users)} 個):")
            for user in all_users:
                print(f"   ID: {user.id}, 用戶名: '{user.username}', Email: '{user.email}', 角色: {user.role.value}")
            return
        
        print(f"✅ 找到管理員用戶:")
        print(f"   ID: {admin_user.id}")
        print(f"   用戶名: '{admin_user.username}'")
        print(f"   Email: '{admin_user.email}'")
        print(f"   角色: {admin_user.role.value}")
        print(f"   是否啟用: {admin_user.is_active}")
        print(f"   是否驗證: {admin_user.is_verified}")
        
        # 測試密碼驗證
        test_password = "admin123"
        is_valid = admin_user.verify_password(test_password)
        print(f"   密碼 '{test_password}' 驗證: {'✅ 正確' if is_valid else '❌ 錯誤'}")
        
        # 如果密碼錯誤，重設密碼
        if not is_valid:
            print(f"🔄 重設管理員密碼為 '{test_password}'...")
            admin_user.set_password(test_password)
            db.commit()
            print("✅ 密碼重設成功")
            
            # 再次驗證
            is_valid_after = admin_user.verify_password(test_password)
            print(f"   重設後密碼驗證: {'✅ 正確' if is_valid_after else '❌ 錯誤'}")
            
    except Exception as e:
        print(f"❌ 除錯過程中發生錯誤: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    debug_login() 