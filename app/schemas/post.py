from typing import Optional, List
from pydantic import validator
from app.schemas.base import BaseSchema, BaseResponseSchema, SlugSchema
from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse


class PostBase(BaseSchema):
    title: str
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: bool = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class PostCreate(PostBase):
    category_ids: Optional[List[int]] = []
    tag_ids: Optional[List[int]] = []
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('文章標題不能為空')
        return v.strip()
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('文章內容不能為空')
        return v.strip()


class PostUpdate(BaseSchema):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


class PostResponse(PostBase, BaseResponseSchema, SlugSchema):
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = []


class PostListResponse(BaseSchema):
    """文章列表回應（簡化版）"""
    id: int
    title: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: bool
    slug: str
    created_at: str
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = [] 