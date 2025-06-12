from typing import Optional
from decimal import Decimal
from pydantic import validator
from app.schemas.base import BaseSchema, BaseResponseSchema, SlugSchema


class ProductBase(BaseSchema):
    name: str
    description: str
    short_description: Optional[str] = None
    price: Decimal
    sale_price: Optional[Decimal] = None
    stock_quantity: int = 0
    sku: Optional[str] = None
    featured_image: Optional[str] = None
    gallery_images: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductCreate(ProductBase):
    pass
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('商品名稱不能為空')
        return v.strip()
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('商品描述不能為空')
        return v.strip()
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('價格必須大於 0')
        return v
    
    @validator('sale_price')
    def sale_price_validation(cls, v, values):
        if v is not None:
            if v <= 0:
                raise ValueError('特價必須大於 0')
            if 'price' in values and v >= values['price']:
                raise ValueError('特價必須小於原價')
        return v


class ProductUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    sku: Optional[str] = None
    featured_image: Optional[str] = None
    gallery_images: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductResponse(ProductBase, BaseResponseSchema, SlugSchema):
    current_price: Decimal
    is_on_sale: bool


class ProductListResponse(BaseResponseSchema, SlugSchema):
    """商品列表回應（簡化版）"""
    name: str
    short_description: Optional[str] = None
    price: Decimal
    sale_price: Optional[Decimal] = None
    featured_image: Optional[str] = None
    stock_quantity: int
    is_active: bool
    is_featured: bool
    current_price: Decimal
    is_on_sale: bool
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = [] 