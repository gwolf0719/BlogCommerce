from typing import Optional, List
from decimal import Decimal
from pydantic import validator, Field
from app.schemas.base import BaseSchema, BaseResponseSchema, SlugSchema


class ProductBase(BaseSchema):
    """
    商品基礎 Schema 類別
    
    包含所有商品資料的基本欄位，用於創建和回應的共同結構。
    """
    name: str = Field(..., description="商品名稱", min_length=1, max_length=255)
    description: str = Field(..., description="商品詳細描述", min_length=1)
    short_description: Optional[str] = Field(None, description="商品簡短描述", max_length=500)
    price: Decimal = Field(..., description="商品原價", ge=0)
    sale_price: Optional[Decimal] = Field(None, description="商品特價（如果有）", ge=0)
    stock_quantity: int = Field(0, description="庫存數量", ge=0)
    sku: Optional[str] = Field(None, description="商品貨號/SKU", max_length=100)
    featured_image: Optional[str] = Field(None, description="主要商品圖片 URL")
    gallery_images: Optional[str] = Field(None, description="商品圖庫（JSON 格式）")
    is_active: bool = Field(True, description="商品是否啟用")
    is_featured: bool = Field(False, description="是否為推薦商品")
    meta_title: Optional[str] = Field(None, description="SEO 標題", max_length=255)
    meta_description: Optional[str] = Field(None, description="SEO 描述", max_length=500)
    meta_keywords: Optional[str] = Field(None, description="SEO 關鍵字", max_length=255)


class ProductCreate(ProductBase):
    """
    商品創建 Schema 類別
    
    用於創建新商品的請求結構，包含所有必要的驗證規則。
    
    驗證規則：
    - 商品名稱和描述不能為空
    - 價格必須大於 0
    - 特價必須小於原價
    """
    
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
    """
    商品更新 Schema 類別
    
    用於更新現有商品的請求結構，所有欄位都是可選的。
    只有提供的欄位會被更新。
    """
    name: Optional[str] = Field(None, description="商品名稱", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="商品詳細描述", min_length=1)
    short_description: Optional[str] = Field(None, description="商品簡短描述", max_length=500)
    price: Optional[Decimal] = Field(None, description="商品原價", ge=0)
    sale_price: Optional[Decimal] = Field(None, description="商品特價（如果有）", ge=0)
    stock_quantity: Optional[int] = Field(None, description="庫存數量", ge=0)
    sku: Optional[str] = Field(None, description="商品貨號/SKU", max_length=100)
    featured_image: Optional[str] = Field(None, description="主要商品圖片 URL")
    gallery_images: Optional[str] = Field(None, description="商品圖庫（JSON 格式）")
    is_active: Optional[bool] = Field(None, description="商品是否啟用")
    is_featured: Optional[bool] = Field(None, description="是否為推薦商品")
    meta_title: Optional[str] = Field(None, description="SEO 標題", max_length=255)
    meta_description: Optional[str] = Field(None, description="SEO 描述", max_length=500)
    meta_keywords: Optional[str] = Field(None, description="SEO 關鍵字", max_length=255)


class ProductResponse(ProductBase, BaseResponseSchema, SlugSchema):
    """
    商品詳細資訊回應 Schema 類別
    
    用於回應商品詳細資訊的結構，包含所有商品資料以及額外的計算欄位。
    
    額外欄位：
    - view_count: 商品瀏覽次數
    - current_price: 當前實際價格（特價優先）
    - is_on_sale: 是否正在特價
    - slug: SEO 友好的 URL 別名
    """
    view_count: int = Field(0, description="商品瀏覽次數")
    current_price: Decimal = Field(..., description="當前實際價格（特價優先）")
    is_on_sale: bool = Field(..., description="是否正在特價")


class ProductListResponse(BaseResponseSchema, SlugSchema):
    """
    商品列表回應 Schema 類別（簡化版）
    
    用於商品列表 API 的回應結構，包含必要的商品資訊以提升列表載入效能。
    排除了較大的欄位如詳細描述、圖庫等。
    """
    name: str = Field(..., description="商品名稱")
    short_description: Optional[str] = Field(None, description="商品簡短描述")
    price: Decimal = Field(..., description="商品原價")
    sale_price: Optional[Decimal] = Field(None, description="商品特價（如果有）")
    featured_image: Optional[str] = Field(None, description="主要商品圖片 URL")
    stock_quantity: int = Field(..., description="庫存數量")
    is_active: bool = Field(..., description="商品是否啟用")
    is_featured: bool = Field(..., description="是否為推薦商品")
    view_count: int = Field(0, description="商品瀏覽次數")
    current_price: Decimal = Field(..., description="當前實際價格（特價優先）")
    is_on_sale: bool = Field(..., description="是否正在特價") 