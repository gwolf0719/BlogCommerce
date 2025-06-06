import asyncio
from app.database import get_db, init_db
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

async def create_admin():
    # 初始化數據庫
    init_db()
    
    engine = create_engine('sqlite:///./blogcommerce.db')
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 刪除現有管理員（如果存在）
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            db.delete(existing_admin)
            db.commit()
        
        # 創建新管理員
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="管理員",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("管理員帳號創建成功！")
        print("用戶名: admin")
        print("密碼: admin123")
        
    except Exception as e:
        print(f"創建管理員失敗: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_admin()) 