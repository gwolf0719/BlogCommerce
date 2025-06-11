from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.product import Product
# 分類和標籤已移除
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.auth import get_current_admin_user

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=List[ProductListResponse])
def get_products(
    active_only: bool = Query(True, description="僅顯示啟用的商品"),
    featured_only: bool = Query(False, description="僅顯示推薦商品"),
    category_id: Optional[int] = Query(None, description="按分類過濾"),
    tag_id: Optional[int] = Query(None, description="按標籤過濾"),
    search: Optional[str] = Query(None, description="搜尋商品名稱或描述"),
    min_price: Optional[float] = Query(None, description="最低價格"),
    max_price: Optional[float] = Query(None, description="最高價格"),
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(20, ge=1, le=100, description="限制項目數"),
    db: Session = Depends(get_db)
):
    """取得商品列表"""
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if featured_only:
        query = query.filter(Product.is_featured == True)
    
    if category_id:
        query = query.join(Product.categories).filter(Category.id == category_id)
    
    if tag_id:
        query = query.join(Product.tags).filter(Tag.id == tag_id)
    
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


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """取得單一商品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.get("/slug/{slug}", response_model=ProductResponse)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    """透過 slug 取得商品"""
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.post("/", response_model=ProductResponse)
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
    product_data = product.model_dump(exclude={"category_ids", "tag_ids"})
    db_product = Product(**product_data)
    db_product.slug = db_product.generate_slug(product.name)
    
    # 檢查 slug 是否重複
    slug_exists = db.query(Product).filter(Product.slug == db_product.slug).first()
    if slug_exists:
        import time
        db_product.slug = f"{db_product.slug}-{int(time.time())}"
    
    db.add(db_product)
    db.flush()  # 先取得 ID
    
    # 處理分類關聯
    if product.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(product.category_ids),
            Category.type == CategoryType.PRODUCT
        ).all()
        db_product.categories = categories
    
    # 處理標籤關聯
    if product.tag_ids:
        tags = db.query(Tag).filter(
            Tag.id.in_(product.tag_ids),
            Tag.type == TagType.PRODUCT
        ).all()
        db_product.tags = tags
    
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
    
    # 處理分類和標籤更新
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")
        if category_ids is not None:
            categories = db.query(Category).filter(
                Category.id.in_(category_ids),
                Category.type == CategoryType.PRODUCT
            ).all()
            product.categories = categories
    
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tags = db.query(Tag).filter(
                Tag.id.in_(tag_ids),
                Tag.type == TagType.PRODUCT
            ).all()
            product.tags = tags
    
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


@router.get("/{product_id}/related", response_model=List[ProductListResponse])
def get_related_products(
    product_id: int,
    limit: int = Query(4, ge=1, le=20, description="限制項目數"),
    db: Session = Depends(get_db)
):
    """取得相關商品"""
    # 取得當前商品
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 取得同分類的其他商品
    query = db.query(Product).filter(
        Product.id != product_id,
        Product.is_active == True
    )
    
    # 如果有分類，優先取得同分類商品
    if product.categories:
        category_ids = [cat.id for cat in product.categories]
        query = query.join(Product.categories).filter(
            Category.id.in_(category_ids)
        )
    
    related_products = query.order_by(Product.is_featured.desc(), Product.created_at.desc()).limit(limit).all()
    
    # 如果同分類商品不足，補足其他商品
    if len(related_products) < limit:
        remaining = limit - len(related_products)
        related_ids = [p.id for p in related_products]
        
        additional_products = db.query(Product).filter(
            Product.id != product_id,
            Product.is_active == True,
            Product.id.notin_(related_ids) if related_ids else True
        ).order_by(Product.is_featured.desc(), Product.created_at.desc()).limit(remaining).all()
        
        related_products.extend(additional_products)
    
    return related_products 