from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class PromoUsage(BaseModel):
    """推薦碼使用記錄資料表"""
    __tablename__ = "promo_usages"
    
    # 推薦碼關聯
    promo_code_id = Column(Integer, ForeignKey('promo_codes.id'), nullable=False, comment="推薦碼ID")
    
    # 使用者關聯（可選，支援訪客使用）
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment="使用者ID")
    
    # 訂單關聯
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, comment="訂單ID")
    
    # 使用時的推薦資訊
    promo_amount = Column(Numeric(10, 2), nullable=False, comment="實際推薦金額")
    original_amount = Column(Numeric(10, 2), nullable=False, comment="原始訂單金額")
    final_amount = Column(Numeric(10, 2), nullable=False, comment="推薦後金額")
    
    # 使用者IP和設備資訊（用於統計分析）
    user_ip = Column(String(45), nullable=True, comment="使用者IP")
    user_agent = Column(String(500), nullable=True, comment="使用者代理")
    
    # 使用時間
    used_at = Column(DateTime(timezone=True), server_default=func.now(), comment="使用時間")
    
    # 關聯
    promo_code = relationship("PromoCode", back_populates="usages")
    user = relationship("User", back_populates="promo_usages")
    order = relationship("Order", back_populates="promo_usage")
    
    def __repr__(self):
        return f"<PromoUsage {self.promo_code_id} - Order {self.order_id}>"


# 為了向後相容，保留舊的別名
DiscountUsage = PromoUsage 