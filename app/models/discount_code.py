from sqlalchemy import Column, String, Text, Numeric, Integer, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.base import BaseModel


class PromoType(enum.Enum):
    """推薦碼種類"""
    PERCENTAGE = "PERCENTAGE"  # 總價打折
    AMOUNT = "AMOUNT"          # 總價減價
    FREE_SHIPPING = "FREE_SHIPPING"  # 免運


class PromoCode(BaseModel):
    """推薦碼資料表"""
    __tablename__ = "promo_codes"
    
    # 推薦碼（唯一碼）
    code = Column(String(50), unique=True, nullable=False, index=True, comment="推薦碼")
    
    # 推薦專案名稱
    name = Column(String(100), nullable=False, comment="推薦專案名稱")
    
    # 行銷平台來源
    source = Column(String(100), nullable=True, comment="行銷平台來源")
    
    # 推薦種類
    promo_type = Column(Enum(PromoType), nullable=False, comment="推薦種類")
    
    # 推薦的值
    promo_value = Column(Numeric(10, 2), nullable=False, comment="推薦值")
    
    # 時間範圍
    start_date = Column(DateTime(timezone=True), nullable=False, comment="開始時間")
    end_date = Column(DateTime(timezone=True), nullable=False, comment="結束時間")
    
    # 使用限制
    usage_limit = Column(Integer, nullable=True, comment="使用次數限制（NULL表示無限制）")
    used_count = Column(Integer, default=0, nullable=False, comment="已使用次數")
    
    # 最小訂單金額
    min_order_amount = Column(Numeric(10, 2), nullable=True, comment="最小訂單金額")
    
    # 狀態
    is_active = Column(Boolean, default=True, nullable=False, comment="是否啟用")
    
    # 描述
    description = Column(Text, nullable=True, comment="推薦碼描述")
    
    # 關聯
    usages = relationship("PromoUsage", back_populates="promo_code")
    
    def __repr__(self):
        return f"<PromoCode {self.code}>"


# 為了向後相容，保留舊的別名
DiscountCode = PromoCode
DiscountType = PromoType 