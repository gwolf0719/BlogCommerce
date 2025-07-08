from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from app.services.markdown_service import markdown_service
from app.services.view_tracking_service import ViewTrackingService
from app.auth import get_current_admin_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/api/posts", tags=["文章"])


def process_post_content(post: Post) -> dict:
    """處理文章內容，添加 Markdown 渲染結果"""
    post_dict = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "excerpt": post.excerpt,
        "featured_image": post.featured_image,
        "is_published": post.is_published,
        "meta_title": post.meta_title,
        "meta_description": post.meta_description,
        "meta_keywords": post.meta_keywords,
        "slug": post.slug,
        "view_count": post.view_count,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        # 添加 Markdown 處理結果
        "content_html": markdown_service.render(post.content),
        "toc": markdown_service.get_toc(post.content)
    }
    
    # 如果沒有摘要，自動生成
    if not post.excerpt and post.content:
        post_dict["excerpt"] = markdown_service.extract_excerpt(post.content)
    
    return post_dict


@router.get("", response_model=List[PostListResponse])
def get_posts(
    published_only: Optional[bool] = Query(None, description="僅顯示已發布的文章"),
    search: Optional[str] = Query(None, description="搜尋標題或內容"),
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(10, ge=1, le=50, description="限制項目數"),
    db: Session = Depends(get_db)
):
    """
    取得文章列表，預設顯示所有（不論發布狀態），除非有指定 published_only
    """
    query = db.query(Post)
    if published_only is not None:
        query = query.filter(Post.is_published == published_only)
    if search:
        query = query.filter(
            Post.title.contains(search) |
            Post.content.contains(search)
        )
    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """取得單一文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 記錄瀏覽量
    ViewTrackingService.record_view(
        db=db,
        content_type="post",
        content_id=post_id,
        user_id=current_user.id if current_user else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")
    )
    
    return process_post_content(post)


@router.get("/slug/{slug}", response_model=PostResponse)
def get_post_by_slug(
    slug: str, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """透過 slug 取得文章"""
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 記錄瀏覽量
    ViewTrackingService.record_view(
        db=db,
        content_type="post",
        content_id=post.id,
        user_id=current_user.id if current_user else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")
    )
    
    return process_post_content(post)


@router.post("", response_model=PostResponse)
def create_post(
    post: PostCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """建立新文章"""
    # 檢查標題是否重複
    existing = db.query(Post).filter(Post.title == post.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="文章標題已存在")
    
    # 建立文章
    post_data = post.model_dump()
    
    # 如果沒有摘要，自動從內容生成
    if not post_data.get('excerpt') and post_data.get('content'):
        post_data['excerpt'] = markdown_service.extract_excerpt(post_data['content'])
    
    db_post = Post(**post_data)
    db_post.slug = db_post.generate_slug(post.title)
    
    # 檢查 slug 是否重複
    slug_exists = db.query(Post).filter(Post.slug == db_post.slug).first()
    if slug_exists:
        import time
        db_post.slug = f"{db_post.slug}-{int(time.time())}"
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return process_post_content(db_post)


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    update_data = post_update.model_dump(exclude_unset=True)
    
    # 如果更新內容但沒有摘要，自動生成摘要
    if "content" in update_data and update_data["content"] and not update_data.get("excerpt"):
        update_data["excerpt"] = markdown_service.extract_excerpt(update_data["content"])
    
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
    return process_post_content(post)


@router.delete("/{post_id}")
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """刪除文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(post)
    db.commit()
    return {"message": "文章已刪除"} 