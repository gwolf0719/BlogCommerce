from sqlalchemy import Column, String, Text, Boolean, Numeric, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, SlugMixin


class Product(BaseModel, SlugMixin):
    __tablename__ = "products"
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(Text, nullable=True)  # 簡短描述
    price = Column(Numeric(10, 2), nullable=False)
    sale_price = Column(Numeric(10, 2), nullable=True)  # 特價
    stock_quantity = Column(Integer, default=0)
    sku = Column(String(100), unique=True, nullable=True)  # 商品編號
    
    # 圖片
    featured_image = Column(String(255), nullable=True)
    gallery_images = Column(Text, nullable=True)  # JSON 格式儲存多圖片
    
    # 商品狀態
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # 推薦商品
    
    # SEO 欄位
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(Text, nullable=True)  # SEO 關鍵字
    
    # 瀏覽統計
    view_count = Column(Integer, default=0, nullable=False)
    
    # 關聯
    order_items = relationship("OrderItem", back_populates="product")
    favorited_by = relationship("Favorite", back_populates="product", cascade="all, delete-orphan")
    
    @property
    def current_price(self):
        """取得目前價格（特價優先）"""
        return self.sale_price if self.sale_price else self.price  # type: ignore
    
    @property
    def is_on_sale(self):
        """是否在特價中"""
        return self.sale_price is not None and self.sale_price < self.price  # type: ignore
    
    def __repr__(self):
        return f"<Product {self.name}>" 