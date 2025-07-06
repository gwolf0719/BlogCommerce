"""
行銷專案模型模組

此模組定義了行銷專案相關的資料庫模型，包括：
- MarketingCampaign: 行銷專案主要模型，用於管理優惠碼系列的生成和分發
- CampaignStatus: 專案狀態枚舉，定義專案的各種狀態

功能特點：
1. 支援專案基本資訊管理（名稱、描述、時間範圍）
2. 優惠券設定管理（類型、折扣方式、金額限制）
3. 數量控制（總數、已生成、已分發、已使用）
4. 狀態管理（草稿、進行中、暫停、完成、取消）
5. 統計功能（使用率、分發率、轉換率）

作者：AI Assistant
創建日期：2024
版本：1.0
"""

from sqlalchemy import Column, String, Text, Boolean, Numeric, Integer, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.base import BaseModel


class CampaignStatus(enum.Enum):
    """行銷專案狀態"""
    DRAFT = "draft"          # 草稿
    ACTIVE = "active"        # 進行中
    PAUSED = "paused"        # 暫停
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class MarketingCampaign(BaseModel):
    """行銷專案模型"""
    __tablename__ = "marketing_campaigns"
    
    # 基本資訊
    name = Column(String(100), nullable=False)  # 專案名稱
    description = Column(Text, nullable=True)  # 專案描述
    
    # 優惠設定
    coupon_prefix = Column(String(20), nullable=False)  # 優惠碼前綴
    coupon_type = Column(String(20), nullable=False)  # 優惠券類型
    discount_type = Column(String(20), nullable=False)  # 折扣類型
    discount_value = Column(Numeric(10, 2), nullable=False)  # 折扣值
    minimum_amount = Column(Numeric(10, 2), nullable=True)  # 最低消費金額
    maximum_discount = Column(Numeric(10, 2), nullable=True)  # 最高折扣金額
    
    # 適用商品（用於單一商品折扣）
    product_id = Column(Integer, nullable=True)
    
    # 時間設定
    campaign_start = Column(DateTime(timezone=True), nullable=False)  # 專案開始時間
    campaign_end = Column(DateTime(timezone=True), nullable=False)  # 專案結束時間
    coupon_valid_from = Column(DateTime(timezone=True), nullable=False)  # 優惠券有效開始時間
    coupon_valid_to = Column(DateTime(timezone=True), nullable=False)  # 優惠券有效結束時間
    
    # 數量設定
    total_coupons = Column(Integer, nullable=False, default=0)  # 總優惠券數量
    initial_coupons = Column(Integer, nullable=False, default=0)  # 初始生成數量
    
    # 狀態
    status = Column(Enum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT)
    is_active = Column(Boolean, default=True)
    
    # 統計資訊
    generated_count = Column(Integer, default=0)  # 已生成優惠券數量
    distributed_count = Column(Integer, default=0)  # 已分發優惠券數量
    used_count = Column(Integer, default=0)  # 已使用優惠券數量
    total_discount_amount = Column(Numeric(10, 2), default=0)  # 總折扣金額
    
    # 關聯
    coupons = relationship("Coupon", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MarketingCampaign {self.name}>"
    
    @property
    def is_active_campaign(self) -> bool:
        """檢查專案是否進行中"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # 確保比較時間都是timezone-aware
        start_time = self.campaign_start  # type: ignore
        end_time = self.campaign_end  # type: ignore
        
        if start_time and start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time and end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
            
        return bool(
            self.is_active and  # type: ignore
            self.status == CampaignStatus.ACTIVE and  # type: ignore
            start_time <= now <= end_time
        )
    
    @property
    def can_generate_more_coupons(self) -> bool:
        """檢查是否還可以生成更多優惠券"""
        return self.generated_count < self.total_coupons  # type: ignore
    
    @property
    def usage_rate(self) -> float:
        """獲取使用率"""
        if self.generated_count == 0:  # type: ignore
            return 0.0
        return (self.used_count / self.generated_count) * 100  # type: ignore
    
    @property
    def distribution_rate(self) -> float:
        """獲取分發率"""
        if self.generated_count == 0:  # type: ignore
            return 0.0
        return (self.distributed_count / self.generated_count) * 100  # type: ignore 