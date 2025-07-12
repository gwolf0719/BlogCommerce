from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import Field, validator
from app.schemas.base import BaseSchema, BaseResponseSchema
from app.models.discount_code import PromoType
from enum import Enum


class PromoTypeEnum(str, Enum):
    """推薦碼種類枚舉"""
    PERCENTAGE = "PERCENTAGE"  # 總價打折
    AMOUNT = "AMOUNT"          # 總價減價
    FREE_SHIPPING = "FREE_SHIPPING"  # 免運


class PromoCodeBase(BaseSchema):
    """推薦碼基礎 Schema"""
    code: str = Field(..., description="推薦碼（唯一識別碼）", min_length=1, max_length=50)
    name: str = Field(..., description="推薦專案名稱", min_length=1, max_length=100)
    source: Optional[str] = Field(None, description="行銷平台來源", max_length=100)
    promo_type: PromoTypeEnum = Field(..., description="推薦種類")
    promo_value: Decimal = Field(..., description="推薦值", gt=0)
    start_date: datetime = Field(..., description="開始時間")
    end_date: datetime = Field(..., description="結束時間")
    usage_limit: Optional[int] = Field(None, description="使用次數限制（NULL表示無限制）", ge=0)
    min_order_amount: Optional[Decimal] = Field(None, description="最小訂單金額", ge=0)
    is_active: bool = Field(True, description="是否啟用")
    description: Optional[str] = Field(None, description="推薦碼描述")
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        """驗證結束時間必須晚於開始時間"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('結束時間必須晚於開始時間')
        return v
    
    @validator('code')
    def code_must_be_alphanumeric(cls, v):
        """驗證推薦碼只能包含字母、數字和特定符號"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('推薦碼只能包含字母、數字、底線和連字符')
        return v.upper()  # 轉換為大寫
    
    @validator('promo_value')
    def validate_promo_value(cls, v, values):
        """驗證推薦值的合理範圍"""
        if 'promo_type' in values:
            if values['promo_type'] == PromoTypeEnum.PERCENTAGE:
                if v <= 0 or v > 100:
                    raise ValueError('百分比推薦值必須在 0 到 100 之間')
            elif values['promo_type'] == PromoTypeEnum.AMOUNT:
                if v <= 0:
                    raise ValueError('固定金額推薦值必須大於 0')
        return v


class PromoCodeCreate(PromoCodeBase):
    """建立推薦碼的 Schema"""
    pass


class PromoCodeUpdate(BaseSchema):
    """更新推薦碼的 Schema"""
    code: Optional[str] = Field(None, description="推薦碼（唯一識別碼）", min_length=1, max_length=50)
    name: Optional[str] = Field(None, description="推薦專案名稱", min_length=1, max_length=100)
    source: Optional[str] = Field(None, description="行銷平台來源", max_length=100)
    promo_type: Optional[PromoTypeEnum] = Field(None, description="推薦種類")
    promo_value: Optional[Decimal] = Field(None, description="推薦值", gt=0)
    start_date: Optional[datetime] = Field(None, description="開始時間")
    end_date: Optional[datetime] = Field(None, description="結束時間")
    usage_limit: Optional[int] = Field(None, description="使用次數限制（NULL表示無限制）", ge=0)
    min_order_amount: Optional[Decimal] = Field(None, description="最小訂單金額", ge=0)
    is_active: Optional[bool] = Field(None, description="是否啟用")
    description: Optional[str] = Field(None, description="推薦碼描述")
    
    @validator('code')
    def code_must_be_alphanumeric(cls, v):
        """驗證推薦碼只能包含字母、數字和特定符號"""
        if v is not None:
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('推薦碼只能包含字母、數字、底線和連字符')
            return v.upper()  # 轉換為大寫
        return v


class PromoCodeResponse(PromoCodeBase, BaseResponseSchema):
    """推薦碼回應 Schema"""
    used_count: int = Field(..., description="已使用次數")
    
    class Config:
        from_attributes = True


class PromoCodeListResponse(BaseResponseSchema):
    """推薦碼列表回應 Schema"""
    code: str = Field(..., description="推薦碼")
    name: str = Field(..., description="推薦專案名稱")
    source: Optional[str] = Field(None, description="行銷平台來源")
    promo_type: PromoTypeEnum = Field(..., description="推薦種類")
    promo_value: Decimal = Field(..., description="推薦值")
    start_date: datetime = Field(..., description="開始時間")
    end_date: datetime = Field(..., description="結束時間")
    usage_limit: Optional[int] = Field(None, description="使用次數限制")
    used_count: int = Field(..., description="已使用次數")
    is_active: bool = Field(..., description="是否啟用")
    
    class Config:
        from_attributes = True


class PromoCodeValidateRequest(BaseSchema):
    """推薦碼驗證請求 Schema"""
    code: str = Field(..., description="推薦碼")
    order_amount: Decimal = Field(..., description="訂單金額", gt=0)


class PromoCodeValidateResponse(BaseSchema):
    """推薦碼驗證回應 Schema"""
    is_valid: bool = Field(..., description="是否有效")
    promo_amount: Decimal = Field(..., description="推薦金額")
    message: str = Field(..., description="驗證訊息")
    promo_code: Optional[PromoCodeResponse] = Field(None, description="推薦碼資訊")


class PromoCodeUsageResponse(BaseResponseSchema):
    """推薦碼使用記錄回應 Schema"""
    promo_code_id: int = Field(..., description="推薦碼ID")
    user_id: Optional[int] = Field(None, description="使用者ID")
    order_id: int = Field(..., description="訂單ID")
    promo_amount: Decimal = Field(..., description="推薦金額")
    original_amount: Decimal = Field(..., description="原始金額")
    final_amount: Decimal = Field(..., description="最終金額")
    used_at: datetime = Field(..., description="使用時間")
    
    class Config:
        from_attributes = True


class PromoCodeUsageListResponse(BaseResponseSchema):
    """推薦碼使用記錄列表回應 Schema"""
    id: int = Field(..., description="記錄ID")
    promo_code_id: int = Field(..., description="推薦碼ID")
    promo_code: str = Field(..., description="推薦碼")
    user_id: Optional[int] = Field(None, description="使用者ID")
    order_id: int = Field(..., description="訂單ID")
    promo_amount: Decimal = Field(..., description="推薦金額")
    original_amount: Decimal = Field(..., description="原始金額")
    final_amount: Decimal = Field(..., description="最終金額")
    used_at: datetime = Field(..., description="使用時間")
    
    class Config:
        from_attributes = True


class PromoCodeStatsResponse(BaseSchema):
    """推薦碼統計回應 Schema"""
    total_codes: int = Field(..., description="總推薦碼數")
    active_codes: int = Field(..., description="啟用推薦碼數")
    total_usage: int = Field(..., description="總使用次數")
    total_promo_amount: float = Field(..., description="總推薦金額")
    most_used_code: Optional[str] = Field(None, description="最常使用的推薦碼")
    most_used_count: int = Field(..., description="最常使用的推薦碼使用次數")


# 向後相容的別名
DiscountTypeEnum = PromoTypeEnum
DiscountCodeBase = PromoCodeBase
DiscountCodeCreate = PromoCodeCreate
DiscountCodeUpdate = PromoCodeUpdate
DiscountCodeResponse = PromoCodeResponse
DiscountCodeListResponse = PromoCodeListResponse
DiscountCodeValidateRequest = PromoCodeValidateRequest
DiscountCodeValidateResponse = PromoCodeValidateResponse
DiscountCodeUsageResponse = PromoCodeUsageResponse
DiscountCodeUsageListResponse = PromoCodeUsageListResponse
DiscountCodeStatsResponse = PromoCodeStatsResponse 