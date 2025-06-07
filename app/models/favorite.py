from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Favorite(BaseModel):
    """用戶收藏商品模型"""
    __tablename__ = "favorites"
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 關聯
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorited_by")
    
    # 確保用戶不能重複收藏同一商品
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),
    )