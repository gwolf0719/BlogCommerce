from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.post import Post
# 分類和標籤已移除
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("/", response_model=List[PostListResponse])
def get_posts(
    published_only: bool = Query(True, description="僅顯示已發布的文章"),
    category_id: Optional[int] = Query(None, description="按分類過濾"),
    tag_id: Optional[int] = Query(None, description="按標籤過濾"),
    search: Optional[str] = Query(None, description="搜尋標題或內容"),
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(10, ge=1, le=50, description="限制項目數"),
    db: Session = Depends(get_db)
):
    """取得文章列表"""
    query = db.query(Post)
    
    if published_only:
        query = query.filter(Post.is_published == True)
    
    if category_id:
        query = query.join(Post.categories).filter(Category.id == category_id)
    
    if tag_id:
        query = query.join(Post.tags).filter(Tag.id == tag_id)
    
    if search:
        query = query.filter(
            Post.title.contains(search) | 
            Post.content.contains(search)
        )
    
    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """取得單一文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


@router.get("/slug/{slug}", response_model=PostResponse)
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    """透過 slug 取得文章"""
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """建立新文章"""
    # 檢查標題是否重複
    existing = db.query(Post).filter(Post.title == post.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="文章標題已存在")
    
    # 建立文章
    post_data = post.model_dump(exclude={"category_ids", "tag_ids"})
    db_post = Post(**post_data)
    db_post.slug = db_post.generate_slug(post.title)
    
    # 檢查 slug 是否重複
    slug_exists = db.query(Post).filter(Post.slug == db_post.slug).first()
    if slug_exists:
        import time
        db_post.slug = f"{db_post.slug}-{int(time.time())}"
    
    db.add(db_post)
    db.flush()  # 先取得 ID
    
    # 處理分類關聯
    if post.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(post.category_ids),
            Category.type == CategoryType.BLOG
        ).all()
        db_post.categories = categories
    
    # 處理標籤關聯
    if post.tag_ids:
        tags = db.query(Tag).filter(
            Tag.id.in_(post.tag_ids),
            Tag.type == TagType.BLOG
        ).all()
        db_post.tags = tags
    
    db.commit()
    db.refresh(db_post)
    return db_post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db)
):
    """更新文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    update_data = post_update.model_dump(exclude_unset=True)
    
    # 處理分類和標籤更新
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")
        if category_ids is not None:
            categories = db.query(Category).filter(
                Category.id.in_(category_ids),
                Category.type == CategoryType.BLOG
            ).all()
            post.categories = categories
    
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tags = db.query(Tag).filter(
                Tag.id.in_(tag_ids),
                Tag.type == TagType.BLOG
            ).all()
            post.tags = tags
    
    # 如果更新標題，需要重新生成 slug
    if "title" in update_data:
        post.slug = post.generate_slug(update_data["title"])
        # 檢查 slug 是否重複
        slug_exists = db.query(Post).filter(
            Post.slug == post.slug,
            Post.id != post_id
        ).first()
        if slug_exists:
            import time
            post.slug = f"{post.slug}-{int(time.time())}"
    
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """刪除文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(post)
    db.commit()
    return {"message": "文章已刪除"} 