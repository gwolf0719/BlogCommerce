from sqlalchemy import Column, String, Text, Boolean, Table, ForeignKey, Numeric, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, SlugMixin


# 商品與分類的多對多關聯表
product_categories = Table(
    'product_categories',
    BaseModel.metadata,
    Column('product_id', ForeignKey('products.id'), primary_key=True),
    Column('category_id', ForeignKey('categories.id'), primary_key=True)
)

# 商品與標籤的多對多關聯表
product_tags = Table(
    'product_tags',
    BaseModel.metadata,
    Column('product_id', ForeignKey('products.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)


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
    
    # 關聯
    categories = relationship("Category", secondary=product_categories, back_populates="products")
    tags = relationship("Tag", secondary=product_tags, back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    favorited_by = relationship("Favorite", back_populates="product", cascade="all, delete-orphan")
    
    @property
    def current_price(self):
        """取得目前價格（特價優先）"""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_on_sale(self):
        """是否在特價中"""
        return self.sale_price is not None and self.sale_price < self.price
    
    def __repr__(self):
        return f"<Product {self.name}>" 