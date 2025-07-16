from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
import bcrypt
import enum
from app.models.base import BaseModel

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    # is_admin = Column(Boolean, default=False) # 已移除此行
    is_verified = Column(Boolean, default=False)
    
    # 修正: 將 default 的值從 UserRole.USER 改為 UserRole.user
    role = Column(Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]), default=UserRole.user)
    
    # 關聯
    orders = relationship("Order", back_populates="user")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    view_logs = relationship("ViewLog", back_populates="user", cascade="all, delete-orphan")
    promo_usages = relationship("PromoUsage", back_populates="user")
    # 向後相容的別名
    discount_usages = relationship("PromoUsage", back_populates="user", viewonly=True)
    
    def set_password(self, password: str):
        """設定密碼（使用 bcrypt）"""
        # bcrypt.gensalt() 預設成本係數 rounds=12，可用 bcrypt.gensalt(rounds=10) 調整
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.hashed_password = hashed.decode("utf-8")
    
    def verify_password(self, password: str) -> bool:
        """驗證密碼（使用 bcrypt）"""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.hashed_password.encode("utf-8")
        )
    
    def __repr__(self):
        return f"<User {self.username}>"
