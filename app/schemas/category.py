from typing import Optional, List
from pydantic import validator, field_serializer
from datetime import datetime
from app.schemas.base import BaseSchema, BaseResponseSchema, SlugSchema
from app.models.category import CategoryType


class CategoryBase(BaseSchema):
    name: str
    description: Optional[str] = None
    type: CategoryType


class CategoryCreate(CategoryBase):
    pass
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('分類名稱不能為空')
        return v.strip()


class CategoryUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[CategoryType] = None


class CategoryResponse(CategoryBase, BaseResponseSchema, SlugSchema):
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        return value.isoformat() if value else None


class CategoryWithCounts(CategoryResponse):
    """包含計數的分類回應"""
    post_count: Optional[int] = 0
    product_count: Optional[int] = 0 