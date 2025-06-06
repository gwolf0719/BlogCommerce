from sqlalchemy import Column, String, Text, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, SlugMixin


# 文章與分類的多對多關聯表
post_categories = Table(
    'post_categories',
    BaseModel.metadata,
    Column('post_id', ForeignKey('posts.id'), primary_key=True),
    Column('category_id', ForeignKey('categories.id'), primary_key=True)
)

# 文章與標籤的多對多關聯表
post_tags = Table(
    'post_tags',
    BaseModel.metadata,
    Column('post_id', ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)


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
    
    # 關聯
    categories = relationship("Category", secondary=post_categories, back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    
    def __repr__(self):
        return f"<Post {self.title}>" 