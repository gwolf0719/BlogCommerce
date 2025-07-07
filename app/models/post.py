from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, SlugMixin


class Post(BaseModel, SlugMixin):
    __tablename__ = "posts"
    
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)  # 摘要
    featured_image = Column(String(255), nullable=True)
    is_published = Column(Boolean, default=False)
    
    # SEO 欄位
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(Text, nullable=True)  # SEO 關鍵字
    
    # 瀏覽統計
    view_count = Column(Integer, default=0, nullable=False)
    
    # 關聯已移除
    
    def __repr__(self):
        return f"<Post {self.title}>" 