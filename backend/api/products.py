from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional

from database import get_db
from models.models import Product, Category, User
from models.schemas import (
    Product as ProductSchema, ProductCreate, ProductUpdate, ProductSummary,
    Category as CategorySchema
)
from api.auth import get_current_admin_user
from utils.helpers import create_slug

router = APIRouter()

@router.get("/", response_model=List[ProductSummary])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    active_only: bool = True,
    featured_only: bool = False,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """取得商品列表"""
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if featured_only:
        query = query.filter(Product.is_featured == True)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(
            or_(
                Product.name.contains(search),
                Product.description.contains(search),
                Product.short_description.contains(search),
                Product.sku.contains(search)
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.order_by(desc(Product.created_at)).offset(skip).limit(limit).all()
    return products

@router.get("/{slug}", response_model=ProductSchema)
async def get_product(slug: str, db: Session = Depends(get_db)):
    """取得單一商品"""
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品已下架"
        )
    
    return product

@router.post("/", response_model=ProductSchema)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """建立新商品"""
    # 產生 slug
    if not product_data.slug or product_data.slug.strip() == "":
        product_data.slug = create_slug(product_data.name)
    
    # 檢查 slug 是否已存在
    existing_product = db.query(Product).filter(Product.slug == product_data.slug).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品 slug 已存在"
        )
    
    # 檢查 SKU 是否已存在
    if product_data.sku:
        existing_sku = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU 已存在"
            )
    
    db_product = Product(**product_data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新商品"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    update_data = product_data.dict(exclude_unset=True)
    
    # 檢查 SKU 唯一性
    if "sku" in update_data and update_data["sku"]:
        existing_sku = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id
        ).first()
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU 已存在"
            )
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """刪除商品"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    db.delete(db_product)
    db.commit()
    return {"message": "商品已刪除"}

@router.patch("/{product_id}/stock")
async def update_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新商品庫存"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    db_product.stock_quantity = max(0, quantity)
    db.commit()
    
    return {
        "product_id": product_id,
        "new_stock": db_product.stock_quantity,
        "message": "庫存已更新"
    }

@router.get("/categories/", response_model=List[CategorySchema])
async def get_product_categories(db: Session = Depends(get_db)):
    """取得商品分類"""
    categories = db.query(Category).order_by(Category.name).all()
    return categories 