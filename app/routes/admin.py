from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_admin_user
from app.models.user import User
from app.models.post import Post
from app.models.product import Product
from app.models.order import Order
# 分類和標籤已移除
from app.models.newsletter import NewsletterSubscriber
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.post import PostResponse, PostCreate, PostUpdate
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.schemas.order import OrderResponse, OrderUpdate, OrderListResponse
# 標籤schemas已移除
from app.schemas.newsletter import (
    NewsletterSubscriberResponse,
    NewsletterSubscriberCreate,
    NewsletterSubscriberUpdate,
)
from app.config import settings
import os
import uuid
from PIL import Image

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


@router.get("/users/stats")
def get_users_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """獲取會員統計數據"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    try:
        today = datetime.now().date()
        
        # 總會員數
        total_users = db.query(func.count(User.id)).scalar() or 0
        
        # 活躍會員（使用is_active狀態）
        active_users = db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar() or 0
        
        # 今日新增會員
        today_new_users = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == today
        ).scalar() or 0
        
        # 管理員數量
        admin_users = db.query(func.count(User.id)).filter(
            User.role == 'admin'
        ).scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "today_new_users": today_new_users,
            "admin_users": admin_users
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取會員統計失敗: {str(e)}")


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
    from sqlalchemy import func, desc, asc
    
    query = db.query(Product)
    
    # 搜尋篩選
    if search:
        query = query.filter(
            Product.name.contains(search) |
            Product.description.contains(search) |
            Product.sku.contains(search)
        )
    
    # 分類篩選已移除
    
    # 狀態篩選
    if status == "active":
        query = query.filter(Product.is_active == True)
    elif status == "inactive":
        query = query.filter(Product.is_active == False)
    elif status == "featured":
        query = query.filter(Product.is_featured == True)
    
    # 排序
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

@router.get("/orders", response_model=List[OrderListResponse])
def get_all_orders_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.orders_per_page, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜尋訂單編號或客戶名稱"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得所有訂單列表（管理員）"""
    from sqlalchemy.orm import selectinload
    
    query = db.query(Order).options(selectinload(Order.items))
    
    if search:
        query = query.filter(
            Order.order_number.contains(search) |
            Order.customer_name.contains(search) |
            Order.customer_email.contains(search)
        )
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    # 轉換為 OrderListResponse 格式
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items_count": len(order.items)
        })
    
    return result


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


# 分類管理功能已移除


# ==============================================
# 統計資訊
# ==============================================

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """取得管理員儀表板統計資訊"""
    from sqlalchemy import func
    from app.models.analytics import PageView
    
    try:
        # 基本統計
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_posts = db.query(func.count(Post.id)).scalar() or 0
        total_products = db.query(func.count(Product.id)).scalar() or 0
        total_orders = db.query(func.count(Order.id)).scalar() or 0
        
        # 訂單統計
        pending_orders = db.query(func.count(Order.id)).filter(
            Order.status.in_(["pending", "confirmed"])
        ).scalar() or 0
        
        # 頁面瀏覽統計
        total_page_views = db.query(func.count(PageView.id)).scalar() or 0
        
        # 商品統計
        active_products = db.query(func.count(Product.id)).filter(
            Product.is_active == True
        ).scalar() or 0
        
        # 已發布文章統計
        published_posts = db.query(func.count(Post.id)).filter(
            Post.is_published == True
        ).scalar() or 0
        
        stats = {
            "total_users": total_users,
            "total_posts": total_posts,
            "published_posts": published_posts,
            "total_products": total_products,
            "active_products": active_products,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "total_page_views": total_page_views
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取統計資料失敗: {str(e)}")


# ==============================================
# AI 設定管理
# ==============================================

@router.put("/settings/ai")
async def update_ai_settings(
    settings_data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新AI設定"""
    from app.models.settings import SystemSettings
    
    try:
        for key, value in settings_data.items():
            if key.startswith('ai_'):
                # 查找現有設定
                setting = db.query(SystemSettings).filter(
                    SystemSettings.key == key
                ).first()
                
                if setting:
                    # 根據數據類型轉換值
                    if setting.data_type == "boolean":
                        setting.value = str(value).lower()
                    else:
                        setting.value = str(value)
                else:
                    # 創建新設定
                    setting = SystemSettings(
                        key=key,
                        value=str(value),
                        category="ai",
                        data_type="boolean" if isinstance(value, bool) else "string"
                    )
                    db.add(setting)
        
        db.commit()
        return {"message": "AI設定更新成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新設定失敗: {str(e)}")


@router.post("/posts/generate")
async def generate_ai_post(
    generation_request: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """使用AI生成文章"""
    from app.services.ai_service import AIService
    
    try:
        user_prompt = generation_request.get("prompt", "")
        title_hint = generation_request.get("title_hint", "")
        generate_image = generation_request.get("generate_image", True)
        
        if not user_prompt:
            raise HTTPException(status_code=400, detail="請提供文章提示詞")
        
        async with AIService() as ai_service:
            if not ai_service.is_ai_enabled():
                raise HTTPException(status_code=400, detail="AI功能未啟用，請先在系統設定中啟用")
            
            result = await ai_service.generate_complete_article(
                user_prompt=user_prompt,
                title_hint=title_hint,
                generate_image=generate_image
            )
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return {
                "success": True,
                "data": result["data"],
                "message": "文章生成成功"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI生成失敗: {str(e)}")


@router.get("/ai/status")
async def get_ai_status(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """檢查AI功能狀態"""
    from app.services.ai_service import AIService
    
    try:
        async with AIService() as ai_service:
            return {
                "ai_enabled": ai_service.is_ai_enabled(),
                "image_generation_enabled": ai_service.is_image_generation_enabled(),
                "settings": ai_service.get_ai_settings()
            }
    except Exception as e:
        return {
            "ai_enabled": False,
            "image_generation_enabled": False,
            "error": str(e)
        }


# 標籤管理功能已移除


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


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user)
):
    """上傳圖片"""
    try:
        # 檢查檔案類型
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="不支援的檔案格式")
        
        # 檢查檔案大小 (5MB)
        if file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="檔案大小不能超過5MB")
        
        # 生成唯一檔名
        file_extension = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # 建立上傳目錄
        upload_dir = "app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 儲存檔案
        file_path = os.path.join(upload_dir, unique_filename)
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 如果是圖片，生成縮圖
        try:
            if file.content_type.startswith("image/"):
                with Image.open(file_path) as img:
                    # 建立縮圖目錄
                    thumbnail_dir = os.path.join(upload_dir, "thumbnails")
                    os.makedirs(thumbnail_dir, exist_ok=True)
                    
                    # 生成縮圖
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
        # 從數據庫獲取所有設定
        settings_db = db.query(SystemSettings).all()
        
        # 轉換為字典格式
        settings_dict = {}
        for setting in settings_db:
            settings_dict[setting.key] = setting.parse_value()
        
        # 設定預設值
        defaults = {
            # 基本設定
            'site_name': 'BlogCommerce',
            'site_tagline': '部落格與電商整合平台',
            'site_description': '一個結合部落格與電商功能的現代化平台',
            'site_url': 'http://localhost:8000',
            'admin_email': 'admin@example.com',
            'timezone': 'Asia/Taipei',
            'language': 'zh-TW',
            'site_logo': '',
            'site_favicon': '',
            
            # 功能開關
            'blog_enabled': True,
            'shop_enabled': True,
            'user_registration': True,
            'comment_enabled': True,
            'search_enabled': True,
            'analytics_enabled': True,
            'newsletter_enabled': False,
            'maintenance_mode': False,
            
            # 郵件設定
            'email_provider': 'smtp',
            'smtp_host': '',
            'smtp_port': 587,
            'smtp_username': '',
            'smtp_password': '',
            'smtp_encryption': 'tls',
            'email_from_name': '',
            'email_from_address': '',
            
            # 數據分析
            'google_analytics_id': '',
            'google_tag_manager_id': '',
            'facebook_pixel_id': '',
            'analytics_retention_days': 365,
            
            # AI 設定
            'openai_api_key': '',
            'ai_model': 'gpt-3.5-turbo',
            'ai_content_generation': False,
            'ai_image_generation': False,
            'ai_temperature': 0.7,
            
            # 安全設定
            'login_attempts_limit': 5,
            'lockout_duration': 15,
            'session_timeout': 24,
            'password_min_length': 8,
            'force_https': False,
            'two_factor_auth': False,
            'allowed_file_types': ['jpg', 'png', 'gif', 'webp'],
            'max_file_size': 10
        }
        
        # 合併預設值和數據庫設定
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
            # 查找現有設定
            setting = db.query(SystemSettings).filter(
                SystemSettings.key == key
            ).first()
            
            # 確定設定分類
            if key.startswith(('blog_', 'shop_', 'user_', 'comment_', 'search_', 'analytics_', 'newsletter_', 'maintenance_')):
                category = "features"
            elif key.startswith(('email_', 'smtp_')):
                category = "email"
            elif key.startswith(('google_', 'facebook_', 'analytics_')):
                category = "analytics"
            elif key.startswith(('openai_', 'ai_')):
                category = "ai"
            elif key.startswith(('login_', 'lockout_', 'session_', 'password_', 'force_', 'two_factor_', 'allowed_', 'max_')):
                category = "security"
            else:
                category = "general"
            
            # 確定數據類型
            if isinstance(value, bool):
                data_type = "boolean"
                str_value = "true" if value else "false"
            elif isinstance(value, int):
                data_type = "integer"
                str_value = str(value)
            elif isinstance(value, float):
                data_type = "float"
                str_value = str(value)
            elif isinstance(value, list):
                data_type = "json"
                import json
                str_value = json.dumps(value)
            else:
                data_type = "string"
                str_value = str(value) if value is not None else ""
            
            # 確定是否公開
            is_public = key.endswith('_enabled') or key in ['blog_enabled', 'shop_enabled', 'user_registration']
            
            if setting:
                # 更新現有設定
                setting.value = str_value
                setting.data_type = data_type
                setting.category = category
                setting.is_public = is_public
            else:
                # 創建新設定
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
        # 這裡可以實現實際的郵件發送邏輯
        # 目前返回成功訊息（模擬）
        return {"message": "測試郵件已發送"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發送測試郵件失敗: {str(e)}")
