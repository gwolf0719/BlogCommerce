from typing import Optional, List
from decimal import Decimal
from pydantic import field_validator
from app.schemas.base import BaseSchema, BaseResponseSchema

class ProductBase(BaseSchema):
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Decimal
    sale_price: Optional[Decimal] = None
    sku: Optional[str] = None
    stock_quantity: int = 0
    is_active: bool = True
    is_featured: bool = False
    featured_image: Optional[str] = None
    gallery_images: Optional[List[str]] = []
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    slug: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None

class ProductResponse(ProductBase, BaseResponseSchema):
    id: int
    view_count: int = 0

    # 【核心修正點】: 為特色圖片加上路徑前綴
    @field_validator('featured_image', mode='before')
    @classmethod
    def add_featured_image_prefix(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith('/static/'):
            return f"/static/images/{v}"
        return v

    # 【核心修正點】: 為圖庫中的所有圖片加上路徑前綴，並處理空字符串
    @field_validator('gallery_images', mode='before')
    @classmethod
    def add_gallery_image_prefix(cls, v) -> List[str]:
        # 處理 None 或空值情況
        if v is None:
            return []
        
        # 處理空字符串
        if isinstance(v, str):
            if v.strip() == '':
                return []
            try:
                import json
                v = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                # 如果不是有效的 JSON，當作單一字符串處理
                return [f"/static/images/{v}"] if v and not v.startswith('/static/') else [v] if v else []
        
        # 處理列表
        if isinstance(v, list):
            return [f"/static/images/{img}" for img in v if img and isinstance(img, str) and not img.startswith('/static/')]
        
        # 其他情況返回空列表
        return []

    class Config:
        from_attributes = True

class ProductListResponse(BaseSchema):
    products: List[ProductResponse]
    total: int
