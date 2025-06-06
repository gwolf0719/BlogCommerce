from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Dict, Any

from database import get_db
from models.models import User, Post, Product, Order, Category, Tag
from api.auth import get_current_admin_user

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """取得管理後台儀表板統計資料"""
    
    # 基本統計
    total_users = db.query(func.count(User.id)).scalar()
    total_posts = db.query(func.count(Post.id)).scalar()
    published_posts = db.query(func.count(Post.id)).filter(Post.is_published == True).scalar()
    total_products = db.query(func.count(Product.id)).scalar()
    active_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_categories = db.query(func.count(Category.id)).scalar()
    total_tags = db.query(func.count(Tag.id)).scalar()
    
    # 訂單統計
    pending_orders = db.query(func.count(Order.id)).filter(Order.status == "pending").scalar()
    processing_orders = db.query(func.count(Order.id)).filter(Order.status == "processing").scalar()
    completed_orders = db.query(func.count(Order.id)).filter(Order.status == "delivered").scalar()
    cancelled_orders = db.query(func.count(Order.id)).filter(Order.status == "cancelled").scalar()
    
    # 收入統計
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == "paid"
    ).scalar() or 0
    
    # 本月收入
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == "paid",
        Order.created_at >= start_of_month
    ).scalar() or 0
    
    # 本週收入
    start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    weekly_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == "paid",
        Order.created_at >= start_of_week
    ).scalar() or 0
    
    # 今日收入
    start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    daily_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == "paid",
        Order.created_at >= start_of_day
    ).scalar() or 0
    
    # 低庫存商品
    low_stock_products = db.query(Product).filter(
        Product.stock_quantity <= 5,
        Product.is_active == True
    ).order_by(Product.stock_quantity).limit(10).all()
    
    # 最新訂單
    recent_orders = db.query(Order).order_by(desc(Order.created_at)).limit(5).all()
    
    # 熱門商品 (基於訂單數量)
    popular_products = db.query(
        Product.id,
        Product.name,
        func.sum(func.coalesce(func.count(Order.id), 0)).label('order_count')
    ).outerjoin(
        Order, Product.id == Order.id  # 這裡需要透過 OrderItem 關聯
    ).group_by(Product.id, Product.name).order_by(desc('order_count')).limit(5).all()
    
    return {
        "overview": {
            "total_users": total_users,
            "total_posts": total_posts,
            "published_posts": published_posts,
            "total_products": total_products,
            "active_products": active_products,
            "total_orders": total_orders,
            "total_categories": total_categories,
            "total_tags": total_tags
        },
        "orders": {
            "pending": pending_orders,
            "processing": processing_orders,
            "completed": completed_orders,
            "cancelled": cancelled_orders,
            "total": total_orders
        },
        "revenue": {
            "total": total_revenue,
            "monthly": monthly_revenue,
            "weekly": weekly_revenue,
            "daily": daily_revenue
        },
        "low_stock_products": [
            {
                "id": product.id,
                "name": product.name,
                "stock": product.stock_quantity,
                "sku": product.sku
            }
            for product in low_stock_products
        ],
        "recent_orders": [
            {
                "id": order.id,
                "order_number": order.order_number,
                "customer_name": order.customer_name,
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at
            }
            for order in recent_orders
        ]
    }

@router.get("/stats/revenue")
async def get_revenue_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """取得收入統計 (最近N天)"""
    start_date = datetime.now() - timedelta(days=days)
    
    # 每日收入統計
    daily_revenue = db.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('revenue'),
        func.count(Order.id).label('orders')
    ).filter(
        Order.payment_status == "paid",
        Order.created_at >= start_date
    ).group_by(func.date(Order.created_at)).order_by('date').all()
    
    return {
        "daily_revenue": [
            {
                "date": str(record.date),
                "revenue": record.revenue or 0,
                "orders": record.orders or 0
            }
            for record in daily_revenue
        ]
    }

@router.get("/stats/products")
async def get_product_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """取得商品統計"""
    
    # 依分類統計商品數量
    category_stats = db.query(
        Category.name,
        func.count(Product.id).label('count')
    ).outerjoin(Product).group_by(Category.id, Category.name).all()
    
    # 商品狀態統計
    active_count = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    inactive_count = db.query(func.count(Product.id)).filter(Product.is_active == False).scalar()
    featured_count = db.query(func.count(Product.id)).filter(Product.is_featured == True).scalar()
    
    # 庫存統計
    in_stock = db.query(func.count(Product.id)).filter(Product.stock_quantity > 0).scalar()
    out_of_stock = db.query(func.count(Product.id)).filter(Product.stock_quantity == 0).scalar()
    low_stock = db.query(func.count(Product.id)).filter(
        Product.stock_quantity > 0,
        Product.stock_quantity <= 5
    ).scalar()
    
    return {
        "by_category": [
            {
                "category": record.name or "未分類",
                "count": record.count
            }
            for record in category_stats
        ],
        "by_status": {
            "active": active_count,
            "inactive": inactive_count,
            "featured": featured_count
        },
        "by_stock": {
            "in_stock": in_stock,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock
        }
    }

@router.get("/stats/posts")
async def get_post_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """取得文章統計"""
    
    # 依分類統計文章數量
    category_stats = db.query(
        Category.name,
        func.count(Post.id).label('count')
    ).outerjoin(Post).group_by(Category.id, Category.name).all()
    
    # 文章狀態統計
    published_count = db.query(func.count(Post.id)).filter(Post.is_published == True).scalar()
    draft_count = db.query(func.count(Post.id)).filter(Post.is_published == False).scalar()
    
    # 依作者統計
    author_stats = db.query(
        User.username,
        func.count(Post.id).label('count')
    ).join(Post).group_by(User.id, User.username).all()
    
    # 最近發布的文章
    recent_posts = db.query(Post).filter(
        Post.is_published == True
    ).order_by(desc(Post.published_at)).limit(5).all()
    
    return {
        "by_category": [
            {
                "category": record.name or "未分類",
                "count": record.count
            }
            for record in category_stats
        ],
        "by_status": {
            "published": published_count,
            "draft": draft_count
        },
        "by_author": [
            {
                "author": record.username,
                "count": record.count
            }
            for record in author_stats
        ],
        "recent_published": [
            {
                "id": post.id,
                "title": post.title,
                "published_at": post.published_at
            }
            for post in recent_posts
        ]
    }

@router.get("/system-info")
async def get_system_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """取得系統資訊"""
    from database import settings
    import sys
    import platform
    
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug
        },
        "database": {
            "type": settings.database_type,
            "url": settings.database_url.split("@")[-1] if "@" in settings.database_url else settings.database_url
        },
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0]
        }
    } 