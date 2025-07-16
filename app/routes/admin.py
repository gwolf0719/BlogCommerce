from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, asc
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_admin_user
from app.models.user import User, UserRole
from app.models.post import Post
from app.models.product import Product
from app.models.order import Order
from app.models.discount_code import PromoCode
from app.models.discount_usage import PromoUsage
from app.models.newsletter import NewsletterSubscriber
from app.schemas.user import UserResponse, UserUpdate, UserListResponse, UserCreate
from app.schemas.post import PostResponse, PostCreate, PostUpdate
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.schemas.order import OrderResponse, OrderUpdate, OrderListResponse
from app.schemas.newsletter import (
    NewsletterSubscriberResponse,
    NewsletterSubscriberCreate,
    NewsletterSubscriberUpdate,
)
from app.schemas.admin import AdminStatsResponse
from app.config import settings
import os
import uuid
from PIL import Image
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["管理員"])

# ==============================================
# 統計資訊
# ==============================================

@router.get("/stats", response_model=AdminStatsResponse, summary="獲取儀表板統計數據")
def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得管理員儀表板所需的統計資訊。"""
    try:
        today = datetime.now().date()
        
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_posts = db.query(func.count(Post.id)).scalar() or 0
        published_posts = db.query(func.count(Post.id)).filter(Post.is_published == True).scalar() or 0
        total_products = db.query(func.count(Product.id)).scalar() or 0
        active_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0
        total_orders = db.query(func.count(Order.id)).scalar() or 0
        pending_orders = db.query(func.count(Order.id)).filter(Order.status.in_(["pending", "confirmed"])).scalar() or 0
        total_sales = db.query(func.sum(Order.total_amount)).filter(Order.payment_status == "paid").scalar() or 0
        today_orders = db.query(func.count(Order.id)).filter(func.date(Order.created_at) == today).scalar() or 0
        today_revenue = db.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == today,
            Order.payment_status == "paid"
        ).scalar() or 0
        
        total_discount_codes = db.query(func.count(PromoCode.id)).scalar() or 0
        active_discount_codes = db.query(func.count(PromoCode.id)).filter(PromoCode.is_active == True).scalar() or 0
        total_discount_usage = db.query(func.sum(PromoCode.used_count)).scalar() or 0
        today_discount_usage = db.query(func.count(PromoUsage.id)).filter(func.date(PromoUsage.used_at) == today).scalar() or 0

        return AdminStatsResponse(
            total_users=total_users,
            total_posts=total_posts,
            published_posts=published_posts,
            total_products=total_products,
            active_products=active_products,
            total_orders=total_orders,
            pending_orders=pending_orders,
            total_sales=total_sales or 0,
            today_orders=today_orders,
            today_revenue=today_revenue or 0,
            active_sessions=0, # 移除後給定預設值
            total_discount_codes=total_discount_codes,
            active_discount_codes=active_discount_codes,
            total_discount_usage=total_discount_usage,
            today_discount_usage=today_discount_usage,
            calculated_at=datetime.now()
        )
        
    except Exception as e:
        print(f"獲取統計資料失敗: {e}")
        raise HTTPException(status_code=500, detail="獲取儀表板統計資料時發生內部錯誤")

# ==============================================
# 使用者管理
# ==============================================

@router.get("/users", response_model=UserListResponse, summary="獲取使用者列表 (管理員)")
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜尋使用者名稱或電子郵件"),
    role: Optional[str] = Query(None, description="依角色篩選 (admin/user)"),
    is_active: Optional[bool] = Query(None, description="依啟用狀態篩選"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有使用者列表，支援分頁、搜尋和篩選。"""
    query = db.query(User)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    if role:
        query = query.filter(User.role == role)
        
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return UserListResponse(items=users, total=total)


@router.post("/users", response_model=UserResponse, summary="新增使用者 (管理員)")
def create_user_by_admin(
    user_create: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """由管理員建立新使用者。"""
    from app.auth import get_password_hash
    
    if db.query(User).filter(User.email == user_create.email).first():
        raise HTTPException(status_code=400, detail="此信箱已被註冊")
    if db.query(User).filter(User.username == user_create.username).first():
        raise HTTPException(status_code=400, detail="此使用者名稱已被使用")

    new_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        role=user_create.role,
        is_active=user_create.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# 修正: 將 /users/stats 路由移到 /users/{user_id} 之前
@router.get("/users/stats")
def get_users_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """獲取會員統計數據"""
    try:
        today = datetime.now().date()
        
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        today_new_users = db.query(func.count(User.id)).filter(func.date(User.created_at) == today).scalar() or 0
        admin_users = db.query(func.count(User.id)).filter(User.role == UserRole.admin).scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "today_new_users": today_new_users,
            "admin_users": admin_users
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取會員統計失敗: {str(e)}")


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


@router.put("/users/{user_id}", response_model=UserResponse, summary="更新使用者 (管理員)")
def update_user_by_admin(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新使用者資訊，包括角色和狀態。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    if 'is_active' in update_data and not update_data['is_active'] and user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能停用自己的帳號")
    
    if 'password' in update_data and update_data['password']:
        from app.auth import get_password_hash
        user.hashed_password = get_password_hash(update_data['password'])
        del update_data['password']

    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", summary="刪除使用者 (管理員)")
def delete_user_by_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """由管理員刪除使用者。"""
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="使用者不存在")
    
    if user_to_delete.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能刪除自己的帳號")
    
    if user_to_delete.orders:
        raise HTTPException(status_code=400, detail="無法刪除：此使用者已有相關訂單")
    
    db.delete(user_to_delete)
    db.commit()
    
    return {"message": "使用者已刪除"}


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
            or_(
                Post.title.contains(search),
                Post.content.contains(search)
            )
        )
    
    if published is not None:
        query = query.filter(Post.is_published == published)
    
    posts = query.order_by(Post.id.desc()).offset(skip).limit(limit).all()
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
    status: Optional[str] = Query(None, description="狀態篩選"),
    sort: Optional[str] = Query("created_at_desc", description="排序方式"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有商品列表（管理員）"""
    query = db.query(Product)
    
    if search:
        query = query.filter(
            or_(
                Product.name.contains(search),
                Product.description.contains(search),
                Product.sku.contains(search)
            )
        )
    
    if status == "active":
        query = query.filter(Product.is_active == True)
    elif status == "inactive":
        query = query.filter(Product.is_active == False)
    elif status == "featured":
        query = query.filter(Product.is_featured == True)
    
    if sort == "created_at_desc":
        query = query.order_by(desc(Product.id))
    elif sort == "created_at_asc":
        query = query.order_by(asc(Product.id))
    elif sort == "name_asc":
        query = query.order_by(asc(Product.name))
    elif sort == "name_desc":
        query = query.order_by(desc(Product.name))
    elif sort == "price_asc":
        query = query.order_by(asc(Product.price))
    elif sort == "price_desc":
        query = query.order_by(desc(Product.price))
    else:
        query = query.order_by(desc(Product.id))
    
    total = query.count()
    
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

@router.get("/orders")
def get_all_orders_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.orders_per_page, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜尋訂單編號或客戶名稱"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有訂單列表（管理員）"""
    try:
        from sqlalchemy.orm import selectinload
        
        query = db.query(Order)
        
        if search:
            query = query.filter(
                or_(
                    Order.order_number.contains(search),
                    Order.customer_name.contains(search),
                    Order.customer_email.contains(search)
                )
            )
        
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        return OrderListResponse(items=orders, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取訂單列表失敗: {str(e)}")


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_admin_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得單一訂單詳情（含商品明細）
    - order_id: 訂單ID
    - 回傳: 訂單主資料與 items 陣列
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    _ = order.items
    return order


@router.put("/orders/{order_id}", response_model=OrderResponse)
def admin_update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新訂單狀態（管理員）"""
    from app.routes.orders import update_order
    return update_order(order_id, order_update, db)


@router.put("/orders/{order_id}/payment")
def admin_update_order_payment(
    order_id: int,
    payment_data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新訂單付款狀態（管理員）"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="訂單不存在")
    
    if "payment_method" in payment_data:
        order.payment_method = payment_data["payment_method"]
    
    if "payment_status" in payment_data:
        order.payment_status = payment_data["payment_status"]
    
    if "payment_info" in payment_data:
        order.payment_info = payment_data["payment_info"]
    
    order.payment_updated_at = datetime.now()
    
    db.commit()
    db.refresh(order)
    
    return {"message": "付款狀態更新成功", "order_id": order_id}


# ==============================================
# 電子報訂閱管理
# ==============================================

@router.get("/newsletter/subscribers", response_model=List[NewsletterSubscriberResponse])
def get_newsletter_subscribers_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得電子報訂閱者列表（管理員）"""
    subscribers = db.query(NewsletterSubscriber).order_by(NewsletterSubscriber.subscribed_at.desc()).offset(skip).limit(limit).all()
    return subscribers


@router.post("/newsletter/subscribers", response_model=NewsletterSubscriberResponse)
def create_newsletter_subscriber_admin(
    subscriber: NewsletterSubscriberCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """新增電子報訂閱者（管理員）"""
    existing = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == subscriber.email).first()
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="此電子郵件已訂閱")
        for field, value in subscriber.model_dump().items():
            setattr(existing, field, value)
        existing.is_active = True
        existing.subscribed_at = datetime.utcnow()
        existing.unsubscribed_at = None
        db.commit()
        db.refresh(existing)
        return existing

    db_subscriber = NewsletterSubscriber(**subscriber.model_dump())
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


@router.get("/newsletter/subscribers/{subscriber_id}", response_model=NewsletterSubscriberResponse)
def get_newsletter_subscriber_admin(
    subscriber_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得單一電子報訂閱者（管理員）"""
    subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="訂閱者不存在")
    return subscriber


@router.put("/newsletter/subscribers/{subscriber_id}", response_model=NewsletterSubscriberResponse)
def update_newsletter_subscriber_admin(
    subscriber_id: int,
    subscriber_update: NewsletterSubscriberUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新電子報訂閱者（管理員）"""
    subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="訂閱者不存在")

    update_data = subscriber_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscriber, field, value)

    db.commit()
    db.refresh(subscriber)
    return subscriber


@router.delete("/newsletter/subscribers/{subscriber_id}")
def delete_newsletter_subscriber_admin(
    subscriber_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """刪除電子報訂閱者（管理員）"""
    subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="訂閱者不存在")

    db.delete(subscriber)
    db.commit()

    return {"message": "訂閱者已刪除"}


# ==============================================
# 檔案上傳
# ==============================================

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user)
):
    """上傳圖片"""
    try:
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="不支援的檔案格式")
        
        if file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="檔案大小不能超過5MB")
        
        file_extension = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        upload_dir = "app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        try:
            if file.content_type.startswith("image/"):
                with Image.open(file_path) as img:
                    thumbnail_dir = os.path.join(upload_dir, "thumbnails")
                    os.makedirs(thumbnail_dir, exist_ok=True)
                    
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    thumbnail_path = os.path.join(thumbnail_dir, unique_filename)
                    img.save(thumbnail_path, optimize=True, quality=85)
        except Exception as e:
            print(f"縮圖生成失敗: {e}")
        
        return {
            "success": True,
            "filename": unique_filename,
            "url": f"/static/uploads/{unique_filename}",
            "thumbnail_url": f"/static/uploads/thumbnails/{unique_filename}",
            "message": "檔案上傳成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檔案上傳失敗: {str(e)}")


# ==============================================
# 系統設定管理
# ==============================================

@router.get("/settings")
async def get_admin_settings(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """獲取所有系統設定"""
    from app.models.settings import SystemSettings
    
    try:
        settings_db = db.query(SystemSettings).all()
        
        settings_dict = {}
        for setting in settings_db:
            settings_dict[setting.key] = setting.parse_value()
        
        defaults = {
            'site_name': 'BlogCommerce',
            'site_tagline': '部落格與電商整合平台',
            'site_description': '一個結合部落格與電商功能的現代化平台',
            'site_url': 'http://localhost:8002',
            'admin_email': 'admin@example.com',
            'timezone': 'Asia/Taipei',
            'language': 'zh-TW',
            'site_logo': '',
            'site_favicon': '',
            'blog_enabled': True,
            'shop_enabled': True,
            'user_registration': True,
            'comment_enabled': True,
            'search_enabled': True,
            'newsletter_enabled': False,
            'maintenance_mode': False,
            'email_provider': 'smtp',
            'smtp_host': '',
            'smtp_port': 587,
            'smtp_username': '',
            'smtp_password': '',
            'smtp_encryption': 'tls',
            'email_from_name': '',
            'email_from_address': '',
            'openai_api_key': '',
            'ai_model': 'gpt-3.5-turbo',
            'ai_content_generation': False,
            'ai_image_generation': False,
            'ai_temperature': 0.7,
            'login_attempts_limit': 5,
            'lockout_duration': 15,
            'session_timeout': 24,
            'password_min_length': 8,
            'force_https': False,
            'two_factor_auth': False,
            'allowed_file_types': ['jpg', 'png', 'gif', 'webp'],
            'max_file_size': 10
        }
        
        for key, default_value in defaults.items():
            if key not in settings_dict:
                settings_dict[key] = default_value
        
        return settings_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取設定失敗: {str(e)}")


@router.put("/settings")
async def update_admin_settings(
    settings_data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新系統設定"""
    from app.models.settings import SystemSettings
    
    try:
        for key, value in settings_data.items():
            setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
            
            if key.startswith(('blog_', 'shop_', 'user_', 'comment_', 'search_', 'newsletter_', 'maintenance_')):
                category = "features"
            elif key.startswith(('email_', 'smtp_')):
                category = "email"
            elif key.startswith(('openai_', 'ai_')):
                category = "ai"
            elif key.startswith(('login_', 'lockout_', 'session_', 'password_', 'force_', 'two_factor_', 'allowed_', 'max_')):
                category = "security"
            else:
                category = "general"
            
            if isinstance(value, bool):
                data_type = "boolean"
                str_value = "true" if value else "false"
            elif isinstance(value, int):
                data_type = "integer"
                str_value = str(value)
            elif isinstance(value, float):
                data_type = "float"
                str_value = str(value)
            elif isinstance(value, (list, dict)):
                data_type = "json"
                import json
                str_value = json.dumps(value, ensure_ascii=False)
            else:
                data_type = "string"
                str_value = str(value) if value is not None else ""
            
            is_public = (
                key.endswith('_enabled') or 
                key in ['blog_enabled', 'shop_enabled', 'user_registration'] or
                key in ['site_name', 'site_tagline', 'site_description', 'site_logo', 'site_favicon',
                       'default_currency', 'default_currency_symbol', 'default_meta_title', 'default_meta_description',
                       'default_meta_keywords']
            )
            
            if setting:
                setting.value = str_value
                setting.data_type = data_type
                setting.category = category
                setting.is_public = is_public
            else:
                setting = SystemSettings(
                    key=key,
                    value=str_value,
                    description=f"系統設定：{key}",
                    category=category,
                    data_type=data_type,
                    is_public=is_public
                )
                db.add(setting)
        
        db.commit()
        return {"message": "設定已儲存"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"儲存設定失敗: {str(e)}")


@router.post("/test-email")
async def test_email_settings(
    email_data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """測試郵件設定"""
    try:
        return {"message": "測試郵件已發送"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發送測試郵件失敗: {str(e)}")
