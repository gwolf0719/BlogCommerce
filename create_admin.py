#!/usr/bin/env python3
"""
創建管理員帳號
"""

import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User, UserRole


def create_admin_user():
    """創建管理員帳號"""
    print("👤 創建管理員帳號...")
    
    db = SessionLocal()
    try:
        # 檢查是否已存在管理員
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if existing_admin:
            print(f"✅ 管理員帳號已存在:")
            print(f"   用戶名: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   角色: {existing_admin.role.value}")
            return existing_admin
        
        # 創建新的管理員帳號
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="系統管理員",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        # 設定密碼
        admin_user.set_password("admin123")
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("🎉 管理員帳號創建成功!")
        print(f"   用戶名: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   密碼: admin123")
        print(f"   角色: {admin_user.role.value}")
        
        return admin_user
        
    except Exception as e:
        db.rollback()
        print(f"❌ 創建管理員帳號失敗: {e}")
        return None
    finally:
        db.close()


def list_all_users():
    """列出所有用戶"""
    print("\n👥 所有用戶列表:")
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("   沒有找到任何用戶")
            return
        
        for user in users:
            print(f"   {user.id}. {user.username} ({user.email}) - {user.role.value}")
            
    except Exception as e:
        print(f"❌ 獲取用戶列表失敗: {e}")
    finally:
        db.close()


def main():
    """主函數"""
    print("👨‍💼 管理員帳號管理工具")
    print("=" * 30)
    
    # 創建管理員帳號
    admin = create_admin_user()
    
    # 列出所有用戶
    list_all_users()
    
    if admin:
        print("\n" + "=" * 30)
        print("💡 您現在可以使用以下資訊登入:")
        print("   用戶名: admin 或 admin@example.com")
        print("   密碼: admin123")


if __name__ == "__main__":
    main() 