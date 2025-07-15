from typing import Optional, List
from pydantic import validator
from app.schemas.base import BaseSchema, BaseResponseSchema, SlugSchema



class PostBase(BaseSchema):
    title: str
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: bool = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class PostCreate(PostBase):
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
    meta_keywords: Optional[str] = None


class PostResponse(PostBase, BaseResponseSchema, SlugSchema):
    view_count: int = 0                 # 瀏覽次數
    content_html: Optional[str] = None  # Markdown 渲染後的 HTML
    toc: Optional[str] = None           # 目錄


class PostSummary(BaseResponseSchema, SlugSchema):
    """文章列表項目摘要"""
    title: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: bool
    view_count: int = 0

    class Config:
        from_attributes = True


class PostListResponse(BaseSchema):
    """文章列表的分頁回應"""
    items: List[PostSummary]
    total: int 