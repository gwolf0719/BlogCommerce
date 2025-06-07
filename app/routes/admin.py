from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_admin_user
from app.models.user import User
from app.models.post import Post
from app.models.product import Product
from app.models.order import Order
from app.models.category import Category
from app.models.tag import Tag
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.post import PostResponse, PostCreate, PostUpdate
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.schemas.order import OrderResponse, OrderUpdate
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])

# ==============================================
# 使用者管理
# ==============================================

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.orders_per_page, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜尋使用者名稱或電子郵件"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有使用者列表（管理員）"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            User.username.contains(search) |
            User.email.contains(search)
        )
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得單一使用者詳情（管理員）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新使用者資訊（管理員）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """啟用/停用使用者帳號（管理員）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能停用自己的帳號")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"message": f"使用者帳號已{'啟用' if user.is_active else '停用'}"}


# ==============================================
# 文章管理
# ==============================================

@router.get("/posts", response_model=List[PostResponse])
def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.posts_per_page, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜尋文章標題或內容"),
    published: Optional[bool] = Query(None, description="過濾發布狀態"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有文章列表（管理員）"""
    query = db.query(Post)
    
    if search:
        query = query.filter(
            Post.title.contains(search) |
            Post.content.contains(search)
        )
    
    if published is not None:
        query = query.filter(Post.is_published == published)
    
    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.post("/posts", response_model=PostResponse)
def admin_create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """建立新文章（管理員）"""
    from app.routes.posts import create_post
    return create_post(post, db)


@router.put("/posts/{post_id}", response_model=PostResponse)
def admin_update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新文章（管理員）"""
    from app.routes.posts import update_post
    return update_post(post_id, post_update, db)


@router.delete("/posts/{post_id}")
def admin_delete_post(
    post_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """刪除文章（管理員）"""
    from app.routes.posts import delete_post
    return delete_post(post_id, db)


# ==============================================
# 商品管理
# ==============================================

@router.get("/products")
def get_all_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜尋商品名稱或描述"),
    category: Optional[str] = Query(None, description="分類篩選"),
    status: Optional[str] = Query(None, description="狀態篩選"),
    sort: Optional[str] = Query("created_at_desc", description="排序方式"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有商品列表（管理員）"""
    from sqlalchemy import func, desc, asc
    
    query = db.query(Product)
    
    # 搜尋篩選
    if search:
        query = query.filter(
            Product.name.contains(search) |
            Product.description.contains(search) |
            Product.sku.contains(search)
        )
    
    # 分類篩選
    if category:
        query = query.join(Product.categories).filter(Category.id == category)
    
    # 狀態篩選
    if status == "active":
        query = query.filter(Product.is_active == True)
    elif status == "inactive":
        query = query.filter(Product.is_active == False)
    elif status == "featured":
        query = query.filter(Product.is_featured == True)
    
    # 排序
    if sort == "created_at_desc":
        query = query.order_by(desc(Product.created_at))
    elif sort == "created_at_asc":
        query = query.order_by(asc(Product.created_at))
    elif sort == "name_asc":
        query = query.order_by(asc(Product.name))
    elif sort == "name_desc":
        query = query.order_by(desc(Product.name))
    elif sort == "price_asc":
        query = query.order_by(asc(Product.price))
    elif sort == "price_desc":
        query = query.order_by(desc(Product.price))
    else:
        query = query.order_by(desc(Product.created_at))
    
    # 計算總數
    total = query.count()
    
    # 分頁
    skip = (page - 1) * page_size
    products = query.offset(skip).limit(page_size).all()
    
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("/products", response_model=ProductResponse)
def admin_create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """建立新商品（管理員）"""
    from app.routes.products import create_product
    return create_product(product, db)


@router.get("/products/{product_id}", response_model=ProductResponse)
def admin_get_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得單一商品詳情（管理員）"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
def admin_update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新商品（管理員）"""
    from app.routes.products import update_product
    return update_product(product_id, product_update, db)


@router.delete("/products/{product_id}")
def admin_delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """刪除商品（管理員）"""
    from app.routes.products import delete_product
    return delete_product(product_id, db)


# ==============================================
# 訂單管理
# ==============================================

@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.orders_per_page, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜尋訂單編號或客戶名稱"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有訂單列表（管理員）"""
    query = db.query(Order)
    
    if search:
        query = query.filter(
            Order.order_number.contains(search) |
            Order.customer_name.contains(search) |
            Order.customer_email.contains(search)
        )
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.put("/orders/{order_id}", response_model=OrderResponse)
def admin_update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新訂單狀態（管理員）"""
    from app.routes.orders import update_order
    return update_order(order_id, order_update, current_user, db)


# ==============================================
# 分類管理
# ==============================================

@router.get("/categories")
def get_all_categories(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有分類列表（管理員）"""
    categories = db.query(Category).order_by(Category.name).all()
    return categories


# ==============================================
# 統計資訊
# ==============================================

@router.get("/stats")
def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得管理員儀表板統計資訊"""
    stats = {
        "total_users": db.query(User).count(),
        "total_posts": db.query(Post).count(),
        "published_posts": db.query(Post).filter(Post.is_published == True).count(),
        "total_products": db.query(Product).count(),
        "active_products": db.query(Product).filter(Product.is_active == True).count(),
        "total_orders": db.query(Order).count(),
        "pending_orders": db.query(Order).filter(Order.status == "pending").count(),
        "total_categories": db.query(Category).count(),
        "total_tags": db.query(Tag).count(),
    }
    
    # 計算總銷售額
    from sqlalchemy import func
    total_sales = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_(["confirmed", "shipped", "delivered"])
    ).scalar() or 0
    
    stats["total_sales"] = float(total_sales)
    
    return stats 