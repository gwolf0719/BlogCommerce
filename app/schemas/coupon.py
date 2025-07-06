from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.coupon import CouponType, DiscountType


class CouponBase(BaseModel):
    """優惠券基礎模型"""
    name: str = Field(..., min_length=1, max_length=100, description="優惠券名稱")
    description: Optional[str] = Field(None, description="優惠券描述")
    coupon_type: CouponType = Field(..., description="優惠券類型")
    discount_type: DiscountType = Field(..., description="折扣類型")
    discount_value: Decimal = Field(..., gt=0, description="折扣值")
    minimum_amount: Optional[Decimal] = Field(None, ge=0, description="最低消費金額")
    maximum_discount: Optional[Decimal] = Field(None, gt=0, description="最高折扣金額")
    product_id: Optional[int] = Field(None, description="適用商品ID（用於單一商品折扣）")
    valid_from: datetime = Field(..., description="有效期開始")
    valid_to: datetime = Field(..., description="有效期結束")
    is_active: bool = Field(True, description="是否啟用")

    @validator('valid_to')
    def validate_valid_to(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('有效期結束時間必須晚於開始時間')
        return v

    @validator('product_id')
    def validate_product_id(cls, v, values):
        if values.get('coupon_type') == CouponType.PRODUCT_DISCOUNT and not v:
            raise ValueError('單一商品折扣必須指定商品ID')
        return v

    @validator('maximum_discount')
    def validate_maximum_discount(cls, v, values):
        if values.get('discount_type') == DiscountType.FIXED and v:
            raise ValueError('固定金額折扣不需要設定最高折扣金額')
        return v


class CouponCreate(CouponBase):
    """建立優惠券"""
    pass


class CouponUpdate(BaseModel):
    """更新優惠券"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    discount_value: Optional[Decimal] = Field(None, gt=0)
    minimum_amount: Optional[Decimal] = Field(None, ge=0)
    maximum_discount: Optional[Decimal] = Field(None, gt=0)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class CouponResponse(CouponBase):
    """優惠券響應"""
    id: int
    code: str
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponListResponse(BaseModel):
    """優惠券列表響應"""
    id: int
    code: str
    name: str
    coupon_type: CouponType
    discount_type: DiscountType
    discount_value: Decimal
    valid_from: datetime
    valid_to: datetime
    is_active: bool
    usage_count: int
    created_at: datetime

    class Config:
        orm_mode = True


class CouponBatchCreate(BaseModel):
    """批次建立優惠券"""
    base_coupon: CouponCreate
    count: int = Field(..., ge=1, le=1000, description="建立數量")
    code_prefix: str = Field(..., min_length=1, max_length=20, description="代碼前綴")
    auto_distribute: bool = Field(False, description="是否自動分發")
    target_users: Optional[List[int]] = Field(None, description="目標用戶ID列表")


class CouponBatchCreateResponse(BaseModel):
    """批次建立優惠券響應"""
    success_count: int
    failed_count: int
    total_count: int
    created_codes: List[str]
    errors: List[str]


class CouponUsageBase(BaseModel):
    """優惠券使用基礎模型"""
    coupon_id: int
    user_id: Optional[int] = None
    order_id: int
    discount_amount: Decimal


class CouponUsageCreate(CouponUsageBase):
    """建立優惠券使用記錄"""
    pass


class CouponUsageResponse(CouponUsageBase):
    """優惠券使用記錄響應"""
    id: int
    used_at: datetime
    coupon: CouponResponse
    user_name: Optional[str] = None
    order_number: str

    class Config:
        orm_mode = True


class CouponDistributionBase(BaseModel):
    """優惠券分發基礎模型"""
    coupon_id: int
    user_id: int
    notes: Optional[str] = None


class CouponDistributionCreate(CouponDistributionBase):
    """建立優惠券分發記錄"""
    pass


class CouponDistributionBatch(BaseModel):
    """批次分發優惠券"""
    coupon_id: int
    user_ids: List[int]
    notes: Optional[str] = None


class CouponDistributionResponse(CouponDistributionBase):
    """優惠券分發記錄響應"""
    id: int
    distributed_at: datetime
    coupon: CouponResponse
    user_name: str
    distributor_name: str

    class Config:
        orm_mode = True


class CouponValidationRequest(BaseModel):
    """優惠券驗證請求"""
    code: str = Field(..., min_length=1, max_length=50)
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    amount: Decimal = Field(..., gt=0)


class CouponValidationResponse(BaseModel):
    """優惠券驗證響應"""
    is_valid: bool
    message: str
    discount_amount: Decimal = Field(default=Decimal('0'))
    free_shipping: bool = Field(default=False)
    coupon: Optional[CouponResponse] = None


class CouponStats(BaseModel):
    """優惠券統計"""
    total_coupons: int
    active_coupons: int
    expired_coupons: int
    used_coupons: int
    unused_coupons: int
    total_discount_amount: Decimal
    by_type: dict
    by_month: dict


class UserCouponResponse(BaseModel):
    """用戶可用優惠券響應"""
    id: int
    code: str
    name: str
    description: Optional[str]
    coupon_type: CouponType
    discount_type: DiscountType
    discount_value: Decimal
    minimum_amount: Optional[Decimal]
    maximum_discount: Optional[Decimal]
    valid_from: datetime
    valid_to: datetime
    is_used: bool = False
    distributed_at: Optional[datetime] = None

    class Config:
        orm_mode = True 