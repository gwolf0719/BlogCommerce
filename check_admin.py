from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///./blogcommerce.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

users = db.query(User).all()
print(f'總共有 {len(users)} 個用戶')
for u in users:
    print(f'ID: {u.id}, 用戶名: {u.username}, 角色: {u.role}, 啟用: {u.is_active}')
db.close() 