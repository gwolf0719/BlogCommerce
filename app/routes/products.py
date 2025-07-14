from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.services.view_tracking_service import ViewTrackingService
from app.auth import get_current_admin_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/products", tags=["商品"])



@router.get(
    "",
    response_model=List[ProductResponse],
    summary="取得商品列表",
    description="""
    取得商品列表，支援多種篩選和搜尋選項。
    
    ## 功能特色
    - 🔍 支援商品名稱和描述的模糊搜尋
    - 💰 支援價格範圍篩選
    - ⭐ 支援篩選推薦商品
    - 📖 支援分頁查詢
    - 🎯 支援啟用/停用商品篩選
    
    ## 使用方式
    - 預設只顯示啟用的商品
    - 可透過 `active_only=false` 查看所有商品
    - 可透過 `featured_only=true` 只查看推薦商品
    - 價格篩選支援設定最低價和最高價
    - 搜尋功能會同時搜尋商品名稱和描述
    
    ## 注意事項
    - 回應結果按商品創建時間倒序排列
    - 限制每次最多查詢 100 筆商品
    - 搜尋功能支援部分關鍵字匹配
    """,
    responses={
        200: {
            "description": "成功取得商品列表",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "精選商品",
                            "short_description": "高品質商品",
                            "price": 100.0,
                            "sale_price": 80.0,
                            "featured_image": "/static/images/product1.jpg",
                            "stock_quantity": 50,
                            "is_active": True,
                            "is_featured": True,
                            "view_count": 125,
                            "current_price": 80.0,
                            "is_on_sale": True,
                            "slug": "selected-product",
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T12:00:00"
                        }
                    ]
                }
            }
        }
    }
)
def get_products(
    active_only: bool = Query(True, description="僅顯示啟用的商品"),
    featured_only: bool = Query(False, description="僅顯示推薦商品"),
    search: Optional[str] = Query(None, description="搜尋商品名稱或描述"),
    min_price: Optional[float] = Query(None, description="最低價格"),
    max_price: Optional[float] = Query(None, description="最高價格"),
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(20, ge=1, le=100, description="限制項目數"),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if featured_only:
        query = query.filter(Product.is_featured == True)
    
    if search:
        query = query.filter(
            Product.name.contains(search) | 
            Product.description.contains(search)
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    return products


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="取得單一商品",
    description="""
    透過商品 ID 取得單一商品的詳細資訊。
    
    ## 功能特色
    - 📊 自動記錄商品瀏覽量
    - 🔍 完整的商品資訊回應
    - 💰 包含價格計算和特價資訊
    - 📈 支援用戶行為追蹤
    
    ## 注意事項
    - 會自動記錄商品瀏覽量
    - 如果用戶已登入，會記錄用戶 ID
    - 支援 IP 位址和 User-Agent 追蹤
    """,
    responses={
        200: {
            "description": "成功取得商品資訊",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "精選商品",
                        "description": "這是一個高品質的商品",
                        "short_description": "高品質商品",
                        "price": 100.0,
                        "sale_price": 80.0,
                        "stock_quantity": 50,
                        "sku": "SKU-001",
                        "featured_image": "/static/images/product1.jpg",
                        "is_active": True,
                        "is_featured": True,
                        "view_count": 125,
                        "current_price": 80.0,
                        "is_on_sale": True,
                        "slug": "selected-product",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        404: {"description": "商品不存在"}
    }
)
def get_product(
    product_id: int, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 記錄瀏覽量
    ViewTrackingService.record_view(
        db=db,
        content_type="product",
        content_id=product_id,
        user_id=current_user.id if current_user else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")
    )
    
    return product


@router.get("/slug/{slug}", response_model=ProductResponse)
def get_product_by_slug(
    slug: str, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """透過 slug 取得商品"""
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 記錄瀏覽量
    ViewTrackingService.record_view(
        db=db,
        content_type="product",
        content_id=product.id,
        user_id=current_user.id if current_user else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")
    )
    
    return product


@router.post("/", response_model=ProductResponse)
@router.post("", response_model=ProductResponse)  # 添加不帶尾隨斜線的路由別名
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """建立新商品（需要管理員權限）"""
    # 檢查 SKU 是否重複
    if product.sku and db.query(Product).filter(Product.sku == product.sku).first():
        raise HTTPException(status_code=400, detail="商品編號已存在")
    
    # 建立商品
    product_data = product.model_dump()
    db_product = Product(**product_data)
    db_product.slug = db_product.generate_slug(product.name)
    
    # 檢查 slug 是否重複
    slug_exists = db.query(Product).filter(Product.slug == db_product.slug).first()
    if slug_exists:
        import time
        db_product.slug = f"{db_product.slug}-{int(time.time())}"
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """更新商品（需要管理員權限）"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    update_data = product_update.model_dump(exclude_unset=True)
    
    # 如果更新名稱，需要重新生成 slug
    if "name" in update_data:
        product.slug = product.generate_slug(update_data["name"])
        # 檢查 slug 是否重複
        slug_exists = db.query(Product).filter(
            Product.slug == product.slug,
            Product.id != product_id
        ).first()
        if slug_exists:
            import time
            product.slug = f"{product.slug}-{int(time.time())}"
    
    # 檢查 SKU 重複
    if "sku" in update_data and update_data["sku"]:
        sku_exists = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id
        ).first()
        if sku_exists:
            raise HTTPException(status_code=400, detail="商品編號已存在")
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """刪除商品（需要管理員權限）"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 檢查是否有相關訂單
    if product.order_items:
        raise HTTPException(
            status_code=400,
            detail="無法刪除：此商品已有相關訂單"
        )
    
    db.delete(product)
    db.commit()
    return {"message": "商品已刪除"}


@router.get("/{product_id}/related", response_model=List[ProductResponse])
def get_related_products(
    product_id: int,
    limit: int = Query(4, ge=1, le=20, description="限制項目數"),
    db: Session = Depends(get_db)
):
    """取得相關商品"""
    current_product = db.query(Product).filter(Product.id == product_id).first()
    if not current_product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 取得其他商品（排除目前商品）
    query = db.query(Product).filter(
        Product.id != product_id,
        Product.is_active == True
    )
    
    # 如果沒有足夠的相關商品，補足其他商品
    other_products = query.order_by(Product.created_at.desc()).limit(limit).all()
    
    return other_products 