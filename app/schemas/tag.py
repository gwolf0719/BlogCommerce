from typing import Optional
from pydantic import validator, field_serializer
from datetime import datetime
from app.schemas.base import BaseSchema, BaseResponseSchema, SlugSchema
from app.models.tag import TagType


class TagBase(BaseSchema):
    name: str
    description: Optional[str] = None
    type: TagType


class TagCreate(TagBase):
    pass
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('標籤名稱不能為空')
        return v.strip()


class TagUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None


class TagResponse(TagBase, BaseResponseSchema, SlugSchema):
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat() if value else None
    
    @field_serializer('updated_at')
    def serialize_updated_at(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None


class TagWithCounts(TagResponse):
    """包含計數的標籤回應"""
    post_count: Optional[int] = 0
    product_count: Optional[int] = 0 