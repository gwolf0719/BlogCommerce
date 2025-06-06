from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.category import Category, CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithCounts

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryWithCounts])
def get_categories(
    type: Optional[CategoryType] = Query(None, description="過濾分類類型"),
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(100, ge=1, le=100, description="限制項目數"),
    db: Session = Depends(get_db)
):
    """取得分類列表"""
    query = db.query(Category)
    
    if type:
        query = query.filter(Category.type == type)
    
    categories = query.offset(skip).limit(limit).all()
    
    # 計算每個分類的文章/商品數量
    result = []
    for category in categories:
        category_data = CategoryWithCounts.model_validate(category)
        if category.type == CategoryType.BLOG:
            category_data.post_count = len(category.posts)
        elif category.type == CategoryType.PRODUCT:
            category_data.product_count = len(category.products)
        result.append(category_data)
    
    return result


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """取得單一分類"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分類不存在")
    return category


@router.get("/slug/{slug}", response_model=CategoryResponse)
def get_category_by_slug(slug: str, db: Session = Depends(get_db)):
    """透過 slug 取得分類"""
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="分類不存在")
    return category


@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """建立新分類"""
    # 檢查名稱是否重複
    existing = db.query(Category).filter(
        Category.name == category.name,
        Category.type == category.type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="同類型的分類名稱已存在")
    
    db_category = Category(**category.model_dump())
    db_category.slug = db_category.generate_slug(category.name)
    
    # 檢查 slug 是否重複
    slug_exists = db.query(Category).filter(Category.slug == db_category.slug).first()
    if slug_exists:
        db_category.slug = f"{db_category.slug}-{db_category.type.value}"
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """更新分類"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分類不存在")
    
    update_data = category_update.model_dump(exclude_unset=True)
    
    # 如果更新名稱，需要重新生成 slug
    if "name" in update_data:
        category.slug = category.generate_slug(update_data["name"])
        # 檢查 slug 是否重複
        slug_exists = db.query(Category).filter(
            Category.slug == category.slug,
            Category.id != category_id
        ).first()
        if slug_exists:
            category.slug = f"{category.slug}-{category.type.value}"
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """刪除分類"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分類不存在")
    
    # 檢查是否有關聯的文章或商品
    if category.posts or category.products:
        raise HTTPException(
            status_code=400,
            detail="無法刪除：此分類下仍有文章或商品"
        )
    
    db.delete(category)
    db.commit()
    return {"message": "分類已刪除"} 