from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ShippingTierBase(BaseModel):
    """
    運費級距基礎 Schema
    
    包含運費級距的基本資訊欄位。
    """
    name: str = Field(..., min_length=1, max_length=100, description="級距名稱")
    description: Optional[str] = Field(None, max_length=500, description="級距描述")
    min_amount: Decimal = Field(..., ge=0, description="最低訂單金額 (包含)")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最高訂單金額 (不包含)，null表示無上限")
    shipping_fee: Decimal = Field(..., ge=0, description="運費金額")
    free_shipping: bool = Field(False, description="是否免運費")
    is_active: bool = Field(True, description="是否啟用")
    sort_order: int = Field(0, description="排序權重，數字越大越優先")
    
    @validator('max_amount')
    def validate_max_amount(cls, v, values):
        """驗證最高金額必須大於最低金額"""
        if v is not None and 'min_amount' in values and v <= values['min_amount']:
            raise ValueError('最高金額必須大於最低金額')
        return v
    
    @validator('shipping_fee')
    def validate_shipping_fee(cls, v, values):
        """驗證免運費時運費金額應為 0"""
        if 'free_shipping' in values and values['free_shipping'] and v > 0:
            raise ValueError('免運費時運費金額應設為 0')
        return v


class ShippingTierCreate(ShippingTierBase):
    """
    建立運費級距 Schema
    
    用於建立新運費級距時的資料驗證。
    """
    pass


class ShippingTierUpdate(BaseModel):
    """
    更新運費級距 Schema
    
    用於更新運費級距時的資料驗證，所有欄位都是可選的。
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="級距名稱")
    description: Optional[str] = Field(None, max_length=500, description="級距描述")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最低訂單金額 (包含)")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最高訂單金額 (不包含)，null表示無上限")
    shipping_fee: Optional[Decimal] = Field(None, ge=0, description="運費金額")
    free_shipping: Optional[bool] = Field(None, description="是否免運費")
    is_active: Optional[bool] = Field(None, description="是否啟用")
    sort_order: Optional[int] = Field(None, description="排序權重，數字越大越優先")
    
    @validator('max_amount')
    def validate_max_amount(cls, v, values):
        """驗證最高金額必須大於最低金額"""
        if v is not None and 'min_amount' in values and values['min_amount'] is not None and v <= values['min_amount']:
            raise ValueError('最高金額必須大於最低金額')
        return v
    
    @validator('shipping_fee')
    def validate_shipping_fee(cls, v, values):
        """驗證免運費時運費金額應為 0"""
        if v is not None and 'free_shipping' in values and values['free_shipping'] and v > 0:
            raise ValueError('免運費時運費金額應設為 0')
        return v


class ShippingTierResponse(ShippingTierBase):
    """
    運費級距回應 Schema
    
    用於 API 回應時的資料格式。
    """
    id: int = Field(..., description="運費級距 ID")
    is_unlimited_max: bool = Field(..., description="是否為無上限級距")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")
    
    class Config:
        from_attributes = True


class ShippingTierListResponse(BaseModel):
    """
    運費級距列表回應 Schema
    
    用於運費級距列表 API 回應時的資料格式。
    """
    id: int = Field(..., description="運費級距 ID")
    name: str = Field(..., description="級距名稱")
    description: Optional[str] = Field(None, description="級距描述")
    min_amount: Decimal = Field(..., description="最低訂單金額")
    max_amount: Optional[Decimal] = Field(None, description="最高訂單金額")
    shipping_fee: Decimal = Field(..., description="運費金額")
    free_shipping: bool = Field(..., description="是否免運費")
    is_active: bool = Field(..., description="是否啟用")
    sort_order: int = Field(..., description="排序權重")
    is_unlimited_max: bool = Field(..., description="是否為無上限級距")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")
    
    class Config:
        from_attributes = True


class ShippingTierStatusToggle(BaseModel):
    """
    運費級距狀態切換 Schema
    
    用於切換運費級距啟用狀態。
    """
    is_active: bool = Field(..., description="是否啟用")


class ShippingCalculationRequest(BaseModel):
    """
    運費計算請求 Schema
    
    用於計算運費的請求參數。
    """
    order_amount: Decimal = Field(..., ge=0, description="訂單金額")


class ShippingCalculationResponse(BaseModel):
    """
    運費計算回應 Schema
    
    用於運費計算結果的回應。
    """
    shipping_fee: Decimal = Field(..., description="運費金額")
    free_shipping: bool = Field(..., description="是否免運費")
    applicable_tier: Optional[ShippingTierResponse] = Field(None, description="適用的運費級距")
    message: str = Field(..., description="計算結果說明")
    
    # 新增的詳細資訊欄位
    max_shipping_fee: Optional[Decimal] = Field(None, description="最高運費（原價）")
    free_shipping_threshold: Optional[Decimal] = Field(None, description="免運費門檻金額")
    amount_needed_for_free_shipping: Optional[Decimal] = Field(None, description="還需要多少錢才能免運費")
    next_tier: Optional[ShippingTierResponse] = Field(None, description="下一個運費級距")


class ShippingTierStats(BaseModel):
    """
    運費級距統計 Schema
    
    用於運費級距統計資料的回應。
    """
    total_tiers: int = Field(..., description="總級距數")
    active_tiers: int = Field(..., description="啟用級距數")
    inactive_tiers: int = Field(..., description="停用級距數")
    free_shipping_tiers: int = Field(..., description="免運費級距數")
    average_shipping_fee: Decimal = Field(..., description="平均運費")
    
    class Config:
        from_attributes = True 