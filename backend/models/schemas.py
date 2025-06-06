from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# 基本 Schema 類別
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# 使用者相關 Schema
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    is_admin: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 分類相關 Schema
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

class Category(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 標籤相關 Schema
class TagBase(BaseModel):
    name: str = Field(..., max_length=50)
    slug: str = Field(..., max_length=50)

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 文章相關 Schema
class PostBase(BaseModel):
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: bool = False
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    category_id: Optional[int] = None

class PostCreate(PostBase):
    tag_ids: Optional[List[int]] = []

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

class Post(PostBase):
    id: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    author: User
    category: Optional[Category]
    tags: List[Tag] = []
    
    class Config:
        from_attributes = True

class PostSummary(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    featured_image: Optional[str]
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    author: User
    category: Optional[Category]
    
    class Config:
        from_attributes = True

# 商品相關 Schema
class ProductBase(BaseModel):
    name: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: float = Field(..., gt=0)
    sale_price: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = Field(None, max_length=100)
    stock_quantity: int = Field(default=0, ge=0)
    featured_image: Optional[str] = None
    gallery_images: Optional[str] = None  # JSON string
    is_active: bool = True
    is_featured: bool = False
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    sale_price: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    featured_image: Optional[str] = None
    gallery_images: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    category_id: Optional[int] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    category: Optional[Category]
    
    class Config:
        from_attributes = True

class ProductSummary(BaseModel):
    id: int
    name: str
    slug: str
    short_description: Optional[str]
    price: float
    sale_price: Optional[float]
    featured_image: Optional[str]
    is_active: bool
    is_featured: bool
    category: Optional[Category]
    
    class Config:
        from_attributes = True

# 訂單項目相關 Schema
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    total_price: float
    product: ProductSummary
    
    class Config:
        from_attributes = True

# 訂單相關 Schema
class OrderBase(BaseModel):
    customer_name: str = Field(..., max_length=100)
    customer_email: EmailStr
    customer_phone: Optional[str] = Field(None, max_length=20)
    shipping_address: Optional[str] = None
    shipping_method: Optional[str] = None
    payment_method: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    shipping_method: Optional[str] = None
    shipping_cost: Optional[float] = None

class Order(OrderBase):
    id: int
    order_number: str
    status: str
    total_amount: float
    shipping_cost: float
    payment_status: str
    created_at: datetime
    updated_at: Optional[datetime]
    user: Optional[User]
    order_items: List[OrderItem] = []
    
    class Config:
        from_attributes = True

class OrderSummary(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: float
    customer_name: str
    customer_email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 購物車項目 Schema
class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class CartItemResponse(BaseModel):
    product: ProductSummary
    quantity: int
    subtotal: float 