from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_admin_user
from app.models.user import User
from app.models.post import Post
from app.models.product import Product

router = APIRouter(tags=["frontend"])
templates = Jinja2Templates(directory="app/templates")

# ==============================================
# 管理後台頁面路由
# ==============================================

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """管理後台首頁"""
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": current_user,
        "active_tab": "dashboard"
    })

@router.get("/admin/posts", response_class=HTMLResponse)
async def admin_posts_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """文章管理頁面"""
    return templates.TemplateResponse("admin/posts.html", {
        "request": request,
        "user": current_user,
        "active_tab": "posts"
    })

@router.get("/admin/posts/new", response_class=HTMLResponse)
async def admin_new_post_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """新增文章頁面"""
    return templates.TemplateResponse("admin/post_form.html", {
        "request": request,
        "user": current_user,
        "active_tab": "posts",
        "post_id": None
    })

@router.get("/admin/posts/{post_id}/edit", response_class=HTMLResponse)
async def admin_edit_post_page(
    request: Request,
    post_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """編輯文章頁面"""
    # 檢查文章是否存在
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return templates.TemplateResponse("admin/post_form.html", {
        "request": request,
        "user": current_user,
        "active_tab": "posts",
        "post_id": post_id
    })

@router.get("/admin/products", response_class=HTMLResponse)
async def admin_products_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """商品管理頁面"""
    return templates.TemplateResponse("admin/products.html", {
        "request": request,
        "user": current_user,
        "active_tab": "products"
    })

@router.get("/admin/products/new", response_class=HTMLResponse)
async def admin_new_product_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """新增商品頁面"""
    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "user": current_user,
        "active_tab": "products",
        "product_id": None
    })

@router.get("/admin/products/{product_id}/edit", response_class=HTMLResponse)
async def admin_edit_product_page(
    request: Request,
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """編輯商品頁面"""
    # 檢查商品是否存在
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "user": current_user,
        "active_tab": "products",
        "product_id": product_id
    })

@router.get("/admin/orders", response_class=HTMLResponse)
async def admin_orders_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """訂單管理頁面"""
    return templates.TemplateResponse("admin/orders.html", {
        "request": request,
        "user": current_user,
        "active_tab": "orders"
    })

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """會員管理頁面"""
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "user": current_user,
        "active_tab": "users"
    })

@router.get("/admin/categories", response_class=HTMLResponse)
async def admin_categories_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """分類管理頁面"""
    return templates.TemplateResponse("admin/categories.html", {
        "request": request,
        "user": current_user,
        "active_tab": "categories"
    })

@router.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """流量分析頁面"""
    return templates.TemplateResponse("admin/analytics.html", {
        "request": request,
        "user": current_user,
        "active_tab": "analytics"
    })

@router.get("/admin/content-analytics", response_class=HTMLResponse)
async def admin_content_analytics_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)
):
    """內容分析頁面"""
    return templates.TemplateResponse("admin/content_analytics.html", {
        "request": request,
        "user": current_user,
        "active_tab": "content-analytics"
    })

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """管理員登入頁面"""
    return templates.TemplateResponse("admin/login.html", {
        "request": request
    }) 