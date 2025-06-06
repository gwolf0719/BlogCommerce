from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_engine('sqlite:///./blogcommerce.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

admin = db.query(User).filter(User.username == "admin").first()
if admin:
    print(f'管理員帳號: {admin.username}')
    print(f'密碼哈希: {admin.hashed_password}')
    # 測試常見密碼
    passwords = ['admin', 'admin123', '123456', 'password']
    for pwd in passwords:
        if pwd_context.verify(pwd, admin.hashed_password):
            print(f'密碼是: {pwd}')
            break
    else:
        print('密碼不在常見列表中')
else:
    print('找不到管理員帳號')

db.close() 