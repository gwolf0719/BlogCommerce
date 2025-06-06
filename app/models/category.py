from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel, SlugMixin


class CategoryType(enum.Enum):
    BLOG = "blog"
    PRODUCT = "product"


class Category(BaseModel, SlugMixin):
    __tablename__ = "categories"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(CategoryType), nullable=False)
    
    # 關聯
    posts = relationship("Post", secondary="post_categories", back_populates="categories")
    products = relationship("Product", secondary="product_categories", back_populates="categories")
    
    def __repr__(self):
        return f"<Category {self.name}>" 