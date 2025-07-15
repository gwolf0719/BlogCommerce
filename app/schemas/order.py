from typing import Optional, List, Any
from decimal import Decimal
from datetime import datetime
from pydantic import field_validator, computed_field
from app.schemas.base import BaseSchema, BaseResponseSchema
from app.models.order import OrderStatus
from enum import Enum


class OrderItemBase(BaseSchema):
    product_name: str
    price: Decimal
    quantity: int
    
    @field_validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('數量必須大於 0')
        return v


class OrderItemCreate(BaseSchema):
    product_id: int
    quantity: int
    
    @field_validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('數量必須大於 0')
        return v


class OrderItemResponse(BaseResponseSchema):
    order_id: int
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int

    @computed_field
    @property
    def product_featured_image(self) -> Optional[str]:
        """【核心修正點】: 為圖片檔名加上完整的靜態路徑前綴"""
        if hasattr(self, 'product') and self.product and self.product.featured_image:
            # 確保回傳的是一個完整的、前端可用的 URL 路徑
            return f"/static/images/{self.product.featured_image}"
        # 如果沒有圖片，回傳 None，讓前端可以使用預設圖片
        return None

    @computed_field
    @property
    def product_slug(self) -> Optional[str]:
        if hasattr(self, 'product') and self.product:
            return self.product.slug
        return None
    
    class Config:
        from_attributes = True


class CartItem(BaseSchema):
    product_id: int
    quantity: int


class CartResponse(BaseSchema):
    items: List[OrderItemResponse]
    total_items: int
    total_amount: Decimal


class PaymentMethod(str, Enum):
    transfer = "transfer"
    linepay = "linepay"
    ecpay = "ecpay"
    paypal = "paypal"


class PaymentStatus(str, Enum):
    unpaid = "unpaid"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"
    pending = "pending"
    partial = "partial"


class OrderBase(BaseSchema):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: str
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = PaymentStatus.unpaid
    payment_info: Optional[Any] = None
    payment_updated_at: Optional[datetime] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    
    @field_validator('items')
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('訂單必須包含至少一個商品')
        return v
    
    @field_validator('customer_name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('客戶姓名不能為空')
        return v.strip()
    
    @field_validator('shipping_address')
    def address_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('配送地址不能為空')
        return v.strip()


class OrderUpdate(BaseSchema):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    shipping_address: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None
    payment_info: Optional[Any] = None
    payment_updated_at: Optional[datetime] = None


class OrderResponse(OrderBase, BaseResponseSchema):
    order_number: Optional[str] = None
    user_id: Optional[int] = None
    subtotal: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    total_amount: Decimal
    status: OrderStatus
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderSummary(BaseSchema):
    id: int
    order_number: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    total_amount: Decimal
    status: OrderStatus
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = PaymentStatus.unpaid
    created_at: datetime
    
    @computed_field
    @property
    def items_count(self) -> int:
        if hasattr(self, 'items'):
            return len(self.items)
        return 0

    class Config:
        from_attributes = True


class OrderListResponse(BaseSchema):
    items: List[OrderSummary]
    total: int


class OrderStatusUpdate(BaseSchema):
    status: OrderStatus


class OrderStatsResponse(BaseSchema):
    total_orders: int = 0
    processing_orders: int = 0
    today_orders: int = 0
    total_revenue: Decimal = Decimal("0.00")
