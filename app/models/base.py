from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.sql import func
from app.database import Base
from slugify import slugify


class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SlugMixin:
    """為需要 slug 的模型提供 slug 功能"""
    slug = Column(String(255), unique=True, index=True)
    
    def generate_slug(self, title: str):
        """根據標題生成 slug"""
        base_slug = slugify(title)
        return base_slug 