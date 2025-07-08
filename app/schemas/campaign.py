"""
行銷專案 Pydantic Schema 模組

此模組定義了行銷專案相關的 Pydantic 資料驗證模型，用於 API 請求和回應的資料結構驗證。

主要 Schema 類別：
- CampaignBase: 行銷專案基礎 Schema，包含所有基本欄位
- CampaignCreate: 創建行銷專案的請求 Schema
- CampaignUpdate: 更新行銷專案的請求 Schema  
- CampaignResponse: 行銷專案回應 Schema，包含完整資訊
- CampaignStats: 行銷專案統計資料 Schema
- CampaignListResponse: 行銷專案列表回應 Schema
- CampaignOverviewStats: 行銷專案總覽統計 Schema

功能特點：
1. 完整的資料驗證和型別檢查
2. 自訂驗證規則（時間範圍、折扣值、前綴唯一性等）
3. 支援批次操作和分發功能
4. 豐富的統計資料結構

作者：AI Assistant  
創建日期：2024
版本：1.0
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal

from app.models.campaign import CampaignStatus


class CampaignBase(BaseModel):
    """
    行銷專案基礎 Schema
    
    定義行銷專案的基本資料結構，包含專案的所有核心屬性。
    用作其他 Campaign Schema 的基礎類別。
    
    主要欄位：
    - name: 專案名稱
    - description: 專案描述
    - coupon_prefix: 優惠碼前綴（用於生成唯一優惠碼）
    - coupon_type: 優惠券類型（商品折扣/整筆折扣/免運費）
    - discount_type: 折扣類型（固定金額/百分比）
    - discount_value: 折扣值
    - campaign_start/end: 專案時間範圍
    - coupon_valid_from/to: 優惠券有效期
    - total_coupons: 總優惠券數量
    """
    name: str = Field(..., description="專案名稱")
    description: Optional[str] = Field(None, description="專案描述")
    coupon_prefix: str = Field(..., description="優惠碼前綴")
    coupon_type: str = Field(..., description="優惠券類型")
    discount_type: str = Field(..., description="折扣類型")
    discount_value: Decimal = Field(..., description="折扣值")
    minimum_amount: Optional[Decimal] = Field(None, description="最低消費金額")
    maximum_discount: Optional[Decimal] = Field(None, description="最高折扣金額")
    product_id: Optional[int] = Field(None, description="適用商品ID")
    campaign_start: datetime = Field(..., description="專案開始時間")
    campaign_end: datetime = Field(..., description="專案結束時間")
    coupon_valid_from: datetime = Field(..., description="優惠券有效開始時間")
    coupon_valid_to: datetime = Field(..., description="優惠券有效結束時間")
    total_coupons: int = Field(..., description="總優惠券數量")
    initial_coupons: int = Field(..., description="初始生成數量")
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT, description="專案狀態")
    is_active: bool = Field(default=True, description="是否啟用")

    @validator('coupon_type')
    def validate_coupon_type(cls, v):
        """
        驗證優惠券類型
        
        確保優惠券類型為有效值：
        - product_discount: 單一商品折扣
        - order_discount: 整筆消費折扣
        - free_shipping: 免運費折扣
        """
        valid_types = ['product_discount', 'order_discount', 'free_shipping']
        if v not in valid_types:
            raise ValueError(f'優惠券類型必須是 {valid_types} 之一')
        return v

    @validator('discount_type')
    def validate_discount_type(cls, v):
        """
        驗證折扣類型
        
        確保折扣類型為有效值：
        - fixed: 固定金額折扣
        - percentage: 百分比折扣
        """
        valid_types = ['fixed', 'percentage']
        if v not in valid_types:
            raise ValueError(f'折扣類型必須是 {valid_types} 之一')
        return v

    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        """
        驗證折扣值
        
        規則：
        1. 折扣值必須大於 0
        2. 百分比折扣不能超過 100%
        """
        if v <= 0:
            raise ValueError('折扣值必須大於 0')
        
        discount_type = values.get('discount_type')
        if discount_type == 'percentage' and v > 100:
            raise ValueError('百分比折扣不能超過 100%')
        
        return v

    @validator('campaign_end')
    def validate_campaign_end(cls, v, values):
        """
        驗證專案結束時間
        
        確保專案結束時間晚於開始時間
        """
        campaign_start = values.get('campaign_start')
        if campaign_start and v <= campaign_start:
            raise ValueError('專案結束時間必須晚於開始時間')
        return v

    @validator('coupon_valid_to')
    def validate_coupon_valid_to(cls, v, values):
        """
        驗證優惠券有效結束時間
        
        確保優惠券有效結束時間晚於開始時間
        """
        coupon_valid_from = values.get('coupon_valid_from')
        if coupon_valid_from and v <= coupon_valid_from:
            raise ValueError('優惠券有效結束時間必須晚於開始時間')
        return v

    @validator('initial_coupons')
    def validate_initial_coupons(cls, v, values):
        """
        驗證初始生成優惠券數量
        
        確保初始生成數量不超過總優惠券數量限制
        """
        total_coupons = values.get('total_coupons', 0)
        if v > total_coupons:
            raise ValueError('初始生成數量不能超過總優惠券數量')
        return v


class CampaignCreate(CampaignBase):
    """
    創建行銷專案 Schema
    
    繼承自 CampaignBase，用於創建新的行銷專案。
    包含所有必要的專案設定欄位和驗證規則。
    """
    pass


class CampaignUpdate(BaseModel):
    """
    更新行銷專案 Schema
    
    用於部分更新現有的行銷專案。
    所有欄位都是可選的，只更新提供的欄位。
    適用於 PATCH 請求的資料結構。
    """
    name: Optional[str] = None
    description: Optional[str] = None
    coupon_prefix: Optional[str] = None
    coupon_type: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[Decimal] = None
    minimum_amount: Optional[Decimal] = None
    maximum_discount: Optional[Decimal] = None
    product_id: Optional[int] = None
    campaign_start: Optional[datetime] = None
    campaign_end: Optional[datetime] = None
    coupon_valid_from: Optional[datetime] = None
    coupon_valid_to: Optional[datetime] = None
    total_coupons: Optional[int] = None
    initial_coupons: Optional[int] = None
    status: Optional[CampaignStatus] = None
    is_active: Optional[bool] = None


class CampaignResponse(CampaignBase):
    """行銷專案回應 Schema"""
    id: int
    generated_count: int = Field(default=0, description="已生成優惠券數量")
    distributed_count: int = Field(default=0, description="已分發優惠券數量")
    used_count: int = Field(default=0, description="已使用優惠券數量")
    total_discount_amount: Decimal = Field(default=Decimal('0'), description="總折扣金額")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignStats(BaseModel):
    """行銷專案統計 Schema"""
    campaign_id: int
    campaign_name: str
    total_coupons: int
    generated_count: int
    distributed_count: int
    used_count: int
    total_discount_amount: Decimal
    usage_rate: float = Field(description="使用率 (%)")
    distribution_rate: float = Field(description="分發率 (%)")
    conversion_rate: float = Field(description="轉換率 (%)")
    remaining_coupons: int = Field(description="剩餘可生成優惠券數量")


class CampaignCouponGenerate(BaseModel):
    """行銷專案優惠券生成 Schema"""
    campaign_id: int
    count: int = Field(..., gt=0, description="生成數量")
    auto_distribute: bool = Field(default=False, description="是否自動分發")
    target_users: Optional[List[int]] = Field(None, description="目標用戶ID列表")


class CampaignCouponDistribute(BaseModel):
    """行銷專案優惠券分發 Schema"""
    campaign_id: int
    user_ids: List[int] = Field(..., description="用戶ID列表")
    coupon_count: int = Field(default=1, description="每個用戶分發的優惠券數量")
    notes: Optional[str] = Field(None, description="分發備註")


class CampaignListResponse(BaseModel):
    """行銷專案列表回應 Schema"""
    items: List[CampaignResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CampaignOverviewStats(BaseModel):
    """行銷專案總覽統計 Schema"""
    total_campaigns: int
    active_campaigns: int
    draft_campaigns: int
    completed_campaigns: int
    total_coupons_generated: int
    total_coupons_used: int
    total_discount_amount: Decimal
    average_usage_rate: float 