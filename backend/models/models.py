from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import datetime

# 多對多關聯表：文章和標籤
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# 使用者模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 關聯
    posts = relationship("Post", back_populates="author")
    orders = relationship("Order", back_populates="user")

# 分類模型
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 關聯
    posts = relationship("Post", back_populates="category")
    products = relationship("Product", back_populates="category")

# 標籤模型
class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 關聯
    posts = relationship("Post", secondary=post_tags, back_populates="tags")

# 文章模型
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    featured_image = Column(String(255))
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # SEO 相關
    meta_title = Column(String(60))
    meta_description = Column(String(160))
    
    # 外鍵
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # 關聯
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

# 商品模型
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    short_description = Column(Text)
    price = Column(Float, nullable=False)
    sale_price = Column(Float)
    sku = Column(String(100), unique=True)
    stock_quantity = Column(Integer, default=0)
    featured_image = Column(String(255))
    gallery_images = Column(Text)  # JSON string
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # SEO 相關
    meta_title = Column(String(60))
    meta_description = Column(String(160))
    
    # 外鍵
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # 關聯
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

# 訂單模型
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default="pending")  # pending, processing, shipped, delivered, cancelled
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 客戶資訊
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)
    customer_phone = Column(String(20))
    
    # 配送資訊
    shipping_address = Column(Text)
    shipping_method = Column(String(50))
    shipping_cost = Column(Float, default=0)
    
    # 付款資訊
    payment_method = Column(String(50))
    payment_status = Column(String(20), default="pending")  # pending, paid, failed, refunded
    
    # 外鍵
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 關聯
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

# 訂單項目模型
class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # 外鍵
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # 關聯
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items") 