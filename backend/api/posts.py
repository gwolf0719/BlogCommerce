from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional
from datetime import datetime

from database import get_db, settings
from models.models import Post, User, Category, Tag
from models.schemas import (
    Post as PostSchema, PostCreate, PostUpdate, PostSummary,
    Category as CategorySchema, CategoryCreate, CategoryUpdate,
    Tag as TagSchema, TagCreate
)
from api.auth import get_current_admin_user
from utils.helpers import create_slug

router = APIRouter()

# 文章相關端點
@router.get("/", response_model=List[PostSummary])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    search: Optional[str] = None,
    published_only: bool = True,
    db: Session = Depends(get_db)
):
    """取得文章列表"""
    query = db.query(Post)
    
    if published_only:
        query = query.filter(Post.is_published == True)
    
    if category_id:
        query = query.filter(Post.category_id == category_id)
    
    if tag_id:
        query = query.join(Post.tags).filter(Tag.id == tag_id)
    
    if search:
        query = query.filter(
            or_(
                Post.title.contains(search),
                Post.content.contains(search),
                Post.excerpt.contains(search)
            )
        )
    
    posts = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    return posts

@router.get("/{slug}", response_model=PostSchema)
async def get_post(slug: str, db: Session = Depends(get_db)):
    """取得單一文章"""
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 如果文章未發布，需要管理員權限
    if not post.is_published:
        # 這裡可以加入權限檢查
        pass
    
    return post

@router.post("/", response_model=PostSchema)
async def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """建立新文章"""
    # 產生 slug
    if not post_data.slug or post_data.slug.strip() == "":
        post_data.slug = create_slug(post_data.title)
    
    # 檢查 slug 是否已存在
    existing_post = db.query(Post).filter(Post.slug == post_data.slug).first()
    if existing_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文章 slug 已存在"
        )
    
    # 建立文章
    db_post = Post(
        title=post_data.title,
        slug=post_data.slug,
        content=post_data.content,
        excerpt=post_data.excerpt,
        featured_image=post_data.featured_image,
        is_published=post_data.is_published,
        meta_title=post_data.meta_title,
        meta_description=post_data.meta_description,
        author_id=current_user.id,
        category_id=post_data.category_id
    )
    
    if post_data.is_published:
        db_post.published_at = datetime.utcnow()
    
    db.add(db_post)
    db.commit()
    
    # 處理標籤
    if post_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(post_data.tag_ids)).all()
        db_post.tags = tags
        db.commit()
    
    db.refresh(db_post)
    return db_post

@router.put("/{post_id}", response_model=PostSchema)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新文章"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 更新欄位
    update_data = post_data.dict(exclude_unset=True)
    
    # 處理標籤
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            db_post.tags = tags
    
    # 如果變更為發布狀態，設定發布時間
    if update_data.get("is_published") and not db_post.is_published:
        update_data["published_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """刪除文章"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    db.delete(db_post)
    db.commit()
    return {"message": "文章已刪除"}

# 分類相關端點
@router.get("/categories/", response_model=List[CategorySchema])
async def get_categories(db: Session = Depends(get_db)):
    """取得所有分類"""
    categories = db.query(Category).order_by(Category.name).all()
    return categories

@router.post("/categories/", response_model=CategorySchema)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """建立新分類"""
    # 產生 slug
    if not category_data.slug or category_data.slug.strip() == "":
        category_data.slug = create_slug(category_data.name)
    
    # 檢查名稱和 slug 是否已存在
    existing_category = db.query(Category).filter(
        or_(Category.name == category_data.name, Category.slug == category_data.slug)
    ).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分類名稱或 slug 已存在"
        )
    
    db_category = Category(**category_data.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新分類"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分類不存在"
        )
    
    update_data = category_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """刪除分類"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分類不存在"
        )
    
    # 檢查是否有文章使用此分類
    posts_count = db.query(Post).filter(Post.category_id == category_id).count()
    if posts_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無法刪除分類，仍有 {posts_count} 篇文章使用此分類"
        )
    
    db.delete(db_category)
    db.commit()
    return {"message": "分類已刪除"}

# 標籤相關端點
@router.get("/tags/", response_model=List[TagSchema])
async def get_tags(db: Session = Depends(get_db)):
    """取得所有標籤"""
    tags = db.query(Tag).order_by(Tag.name).all()
    return tags

@router.post("/tags/", response_model=TagSchema)
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """建立新標籤"""
    # 產生 slug
    if not tag_data.slug or tag_data.slug.strip() == "":
        tag_data.slug = create_slug(tag_data.name)
    
    # 檢查名稱和 slug 是否已存在
    existing_tag = db.query(Tag).filter(
        or_(Tag.name == tag_data.name, Tag.slug == tag_data.slug)
    ).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="標籤名稱或 slug 已存在"
        )
    
    db_tag = Tag(**tag_data.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """刪除標籤"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="標籤不存在"
        )
    
    db.delete(db_tag)
    db.commit()
    return {"message": "標籤已刪除"} 