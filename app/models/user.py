from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
import enum
from app.models.base import BaseModel

# 密碼加密設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    
    # 關聯
    orders = relationship("Order", back_populates="user")
    
    def set_password(self, password: str):
        """設定密碼（加密）"""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """驗證密碼"""
        return pwd_context.verify(password, self.hashed_password)
    
    def __repr__(self):
        return f"<User {self.username}>" 