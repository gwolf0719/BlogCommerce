from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel, SlugMixin


class TagType(enum.Enum):
    BLOG = "blog"
    PRODUCT = "product"


class Tag(BaseModel, SlugMixin):
    __tablename__ = "tags"
    
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(TagType), nullable=False)
    
    # 關聯
    posts = relationship("Post", secondary="post_tags", back_populates="tags")
    products = relationship("Product", secondary="product_tags", back_populates="tags")
    
    def __repr__(self):
        return f"<Tag {self.name}>" 