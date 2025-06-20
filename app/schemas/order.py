from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import validator, field_serializer
from app.schemas.base import BaseSchema, BaseResponseSchema
from app.models.order import OrderStatus


class OrderItemBase(BaseSchema):
    product_name: str
    price: Decimal
    quantity: int
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('數量必須大於 0')
        return v


class OrderItemCreate(BaseSchema):
    """建立訂單時使用 product_id，系統會自動填入 product_name 和 price"""
    product_id: int
    quantity: int
    
    @validator('quantity')
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
    
    class Config:
        from_attributes = True


class CartItem(BaseSchema):
    """購物車項目"""
    product_id: int
    quantity: int


class CartResponse(BaseSchema):
    """購物車回應"""
    items: List[OrderItemResponse]
    total_items: int
    total_amount: Decimal


class OrderBase(BaseSchema):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: str
    payment_method: Optional[str] = "credit_card"
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    
    @validator('items')
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('訂單必須包含至少一個商品')
        return v
    
    @validator('customer_name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('客戶姓名不能為空')
        return v.strip()
    
    @validator('shipping_address')
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


class OrderResponse(OrderBase, BaseResponseSchema):
    order_number: Optional[str] = None
    user_id: Optional[int] = None
    subtotal: Optional[Decimal] = None
    shipping_fee: Optional[Decimal] = None
    total_amount: Decimal
    status: OrderStatus
    items: List[OrderItemResponse] = []

    @field_serializer('created_at')
    def serialize_created_at(self, value, _info) -> str:
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, str):
            return value
        else:
            return str(value) if value else None


class OrderListResponse(BaseSchema):
    """訂單列表回應（簡化版）"""
    id: int
    order_number: Optional[str] = None
    customer_name: str
    total_amount: Decimal
    status: OrderStatus
    created_at: str
    items_count: int = 0

    @field_serializer('created_at')
    def serialize_created_at(self, value, _info) -> str:
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, str):
            return value
        else:
            return str(value) if value else None

    @field_serializer('total_amount')
    def serialize_total_amount(self, value, _info) -> str:
        return str(value) if value else "0.00"

    class Config:
        from_attributes = True 