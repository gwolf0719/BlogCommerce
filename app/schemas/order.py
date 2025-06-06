from typing import Optional, List
from decimal import Decimal
from pydantic import validator
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


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase, BaseResponseSchema):
    order_id: int
    product_price: Decimal
    total_price: Optional[Decimal] = None


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


class OrderListResponse(BaseSchema):
    """訂單列表回應（簡化版）"""
    id: int
    order_number: Optional[str] = None
    customer_name: str
    total_amount: Decimal
    status: OrderStatus
    created_at: str
    items_count: int 