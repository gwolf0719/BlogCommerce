"""
優惠券模型模組

此模組定義了優惠券系統相關的資料庫模型，支援多種類型的優惠券和完整的使用記錄追蹤。

主要模型：
- Coupon: 優惠券主要模型，支援多種優惠類型和使用條件
- CouponUsage: 優惠券使用記錄，追蹤實際使用情況
- CouponDistribution: 優惠券分發記錄，管理優惠券的分發歷史

枚舉類別：
- CouponType: 優惠券類型（商品折扣/整筆折扣/免運費）
- DiscountType: 折扣類型（固定金額/百分比）

功能特點：
1. 支援多種優惠券類型（商品特定/整筆消費/免運費）
2. 靈活的折扣計算（固定金額/百分比，含最低消費/最高折扣限制）
3. 時間有效期控制和狀態管理
4. 與行銷專案系統整合
5. 完整的使用記錄和分發追蹤
6. 自動統計使用次數

作者：AI Assistant
創建日期：2024
版本：1.0
"""

from sqlalchemy import Column, String, Text, Boolean, Numeric, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.base import BaseModel


class CouponType(enum.Enum):
    """優惠券類型"""
    PRODUCT_DISCOUNT = "product_discount"      # 單一商品折扣
    ORDER_DISCOUNT = "order_discount"          # 整筆消費折扣
    FREE_SHIPPING = "free_shipping"            # 免運費折扣


class DiscountType(enum.Enum):
    """折扣類型"""
    FIXED = "fixed"        # 固定金額
    PERCENTAGE = "percentage"  # 百分比


class Coupon(BaseModel):
    """優惠券模型"""
    __tablename__ = "coupons"
    
    # 基本資訊
    code = Column(String(50), unique=True, nullable=False, index=True)  # 優惠券代碼
    name = Column(String(100), nullable=False)  # 優惠券名稱
    description = Column(Text, nullable=True)  # 優惠券描述
    
    # 優惠券類型和折扣設定
    coupon_type = Column(Enum(CouponType), nullable=False)  # 優惠券類型
    discount_type = Column(Enum(DiscountType), nullable=False)  # 折扣類型
    discount_value = Column(Numeric(10, 2), nullable=False)  # 折扣值
    
    # 使用條件
    minimum_amount = Column(Numeric(10, 2), nullable=True)  # 最低消費金額
    maximum_discount = Column(Numeric(10, 2), nullable=True)  # 最高折扣金額（用於百分比折扣）
    
    # 適用商品（用於單一商品折扣）
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    
    # 行銷專案關聯
    campaign_id = Column(Integer, ForeignKey('marketing_campaigns.id'), nullable=True)
    
    # 使用期限
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_to = Column(DateTime(timezone=True), nullable=False)
    
    # 狀態
    is_active = Column(Boolean, default=True)
    
    # 統計資訊
    usage_count = Column(Integer, default=0)  # 使用次數
    
    # 關聯
    product = relationship("Product", back_populates="coupons")
    campaign = relationship("MarketingCampaign", back_populates="coupons")
    usage_records = relationship("CouponUsage", back_populates="coupon", cascade="all, delete-orphan")
    distributions = relationship("CouponDistribution", back_populates="coupon", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Coupon {self.code}>"
    
    def is_valid(self) -> bool:
        """檢查優惠券是否有效"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # 確保比較時間都是timezone-aware
        valid_from = self.valid_from
        valid_to = self.valid_to
        
        if valid_from and valid_from.tzinfo is None:
            valid_from = valid_from.replace(tzinfo=timezone.utc)
        if valid_to and valid_to.tzinfo is None:
            valid_to = valid_to.replace(tzinfo=timezone.utc)
            
        return bool(
            self.is_active and  # type: ignore
            valid_from <= now <= valid_to  # type: ignore
        )
    
    def can_use_for_product(self, product_id: int) -> bool:
        """檢查是否可以用於特定商品"""
        if self.coupon_type == CouponType.PRODUCT_DISCOUNT:  # type: ignore
            return self.product_id == product_id  # type: ignore
        return True
    
    def calculate_discount(self, amount, product_id=None):
        """計算折扣金額"""
        from decimal import Decimal
        
        if not self.is_valid():
            return Decimal('0')
        
        if self.coupon_type == CouponType.PRODUCT_DISCOUNT and product_id != self.product_id:  # type: ignore
            return Decimal('0')
        
        if self.minimum_amount and amount < self.minimum_amount:  # type: ignore
            return Decimal('0')
        
        if self.coupon_type == CouponType.FREE_SHIPPING:  # type: ignore
            return Decimal('0')  # 免運費不計算金額折扣
        
        if self.discount_type == DiscountType.FIXED:  # type: ignore
            discount = self.discount_value
        else:  # PERCENTAGE
            discount = amount * (self.discount_value / 100)
            if self.maximum_discount:  # type: ignore
                discount = min(discount, self.maximum_discount)  # type: ignore
        
        return min(discount, amount)  # type: ignore


class CouponUsage(BaseModel):
    """優惠券使用記錄"""
    __tablename__ = "coupon_usage"
    
    # 關聯
    coupon_id = Column(Integer, ForeignKey('coupons.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 允許訪客使用
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    
    # 使用資訊
    used_at = Column(DateTime(timezone=True), server_default=func.now())
    discount_amount = Column(Numeric(10, 2), nullable=False)  # 實際折扣金額
    
    # 關聯
    coupon = relationship("Coupon", back_populates="usage_records")
    user = relationship("User", back_populates="coupon_usage")
    order = relationship("Order", back_populates="coupon_usage")
    
    def __repr__(self):
        return f"<CouponUsage {self.coupon_id} by {self.user_id}>"


class CouponDistribution(BaseModel):
    """優惠券分發記錄"""
    __tablename__ = "coupon_distributions"
    
    # 關聯
    coupon_id = Column(Integer, ForeignKey('coupons.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    distributed_by = Column(Integer, ForeignKey('users.id'), nullable=False)  # 分發者
    
    # 分發資訊
    distributed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)  # 分發備註
    
    # 關聯
    coupon = relationship("Coupon", back_populates="distributions")
    user = relationship("User", foreign_keys=[user_id], back_populates="received_coupons")
    distributor = relationship("User", foreign_keys=[distributed_by], back_populates="distributed_coupons")
    
    def __repr__(self):
        return f"<CouponDistribution {self.coupon_id} to {self.user_id}>" 