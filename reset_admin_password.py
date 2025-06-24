#!/usr/bin/env python3
"""
重置管理員密碼腳本
"""

import sys
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.user import User
from app.auth import get_password_hash, verify_password
from app.utils.logger import auth_logger, db_logger
from app.models.user import UserRole

def reset_admin_password(username: str = "admin", new_password: str = "admin123456"):
    """重置管理員密碼"""
    db = SessionLocal()
    try:
        auth_logger.info(f"開始重置管理員密碼: {username}")
        
        # 查找管理員用戶
        admin_user = db.query(User).filter(User.username == username).first()
        
        if not admin_user:
            auth_logger.warning(f"管理員用戶 {username} 不存在，正在創建...")
            
            # 創建新的管理員用戶
            admin_user = User(
                username=username,
                email="admin@example.com",
                hashed_password=get_password_hash(new_password),
                full_name="系統管理員",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            auth_logger.info(f"創建新管理員用戶: {username}")
        else:
            # 更新現有用戶的密碼
            admin_user.hashed_password = get_password_hash(new_password)
            admin_user.is_active = True
            admin_user.role = UserRole.ADMIN
            auth_logger.info(f"更新管理員用戶密碼: {username}")
        
        db.commit()
        
        print(f"✅ 管理員密碼重置成功:")
        print(f"   用戶名: {username}")
        print(f"   密碼: {new_password}")
        print(f"   角色: {admin_user.role}")
        print(f"   狀態: {'啟用' if admin_user.is_active else '停用'}")
        
        auth_logger.info(f"管理員密碼重置完成: {username}")
        
    except Exception as e:
        db.rollback()
        error_msg = f"重置管理員密碼失敗: {e}"
        auth_logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise
    finally:
        db.close()

def verify_admin_login(username: str = "admin", password: str = "admin123456"):
    """驗證管理員登入"""
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"❌ 用戶 {username} 不存在")
            return False
        
        if not verify_password(password, user.hashed_password):
            print(f"❌ 密碼錯誤")
            return False
        
        if not user.is_active:
            print(f"❌ 用戶未啟用")
            return False
        
        if user.role != UserRole.ADMIN:
            print(f"❌ 用戶不是管理員，當前角色: {user.role}")
            return False
        
        print(f"✅ 管理員登入驗證成功")
        print(f"   ID: {user.id}")
        print(f"   用戶名: {user.username}")
        print(f"   郵箱: {user.email}")
        print(f"   全名: {user.full_name}")
        print(f"   角色: {user.role}")
        
        return True
        
    except Exception as e:
        auth_logger.error(f"驗證管理員登入失敗: {e}")
        print(f"❌ 驗證失敗: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 重置管理員密碼...")
    
    try:
        reset_admin_password()
        print("\n🔍 驗證登入...")
        verify_admin_login()
        print("\n🎉 管理員密碼重置和驗證完成！")
        
    except Exception as e:
        print(f"\n❌ 操作失敗: {e}")
        sys.exit(1) 