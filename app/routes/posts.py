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

router = APIRouter(prefix="/posts", tags=["文章"])


def process_post_content(post: Post) -> dict:
    """
    處理文章內容，添加 Markdown 渲染結果
    
    將文章的 Markdown 內容轉換為 HTML，並生成目錄和摘要。
    """
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


@router.get(
    "",
    response_model=List[PostListResponse],
    summary="📄 獲取文章列表",
    description="""
    ## 🎯 功能描述
    獲取部落格文章列表，支援分頁、搜尋和發布狀態篩選。
    
    ## 📋 功能特點
    - 📊 支援分頁查詢
    - 🔍 標題與內容搜尋
    - 📝 發布狀態篩選
    - 🗂️ 時間順序排列
    
    ## 🔍 查詢參數
    - **published_only**: 僅顯示已發布文章
    - **search**: 搜尋標題或內容關鍵字
    - **skip**: 跳過的項目數（分頁）
    - **limit**: 每頁項目數限制
    
    ## 📊 排序規則
    按創建時間降序排列，最新文章在前。
    
    ## 🎯 使用場景
    - 部落格首頁文章列表
    - 管理後台文章管理
    - 搜尋結果展示
    """,
    responses={
        200: {
            "description": "成功獲取文章列表",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "我的第一篇文章",
                            "slug": "my-first-post",
                            "excerpt": "這是文章的摘要...",
                            "featured_image": "https://example.com/image.jpg",
                            "is_published": True,
                            "view_count": 123,
                            "created_at": "2024-01-15T10:30:00",
                            "updated_at": "2024-01-15T10:30:00"
                        }
                    ]
                }
            }
        }
    }
)
def get_posts(
    published_only: Optional[bool] = Query(None, description="僅顯示已發布的文章"),
    search: Optional[str] = Query(None, description="搜尋標題或內容"),
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(10, ge=1, le=50, description="限制項目數"),
    db: Session = Depends(get_db)
):
    """
    取得文章列表，預設顯示所有（不論發布狀態），除非有指定 published_only
    
    支援分頁、搜尋和發布狀態篩選功能。
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


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="📖 獲取單一文章",
    description="""
    ## 🎯 功能描述
    透過文章 ID 獲取完整的文章內容，包含 Markdown 渲染結果。
    
    ## 📋 功能特點
    - 📄 完整文章內容
    - 🎨 Markdown 渲染為 HTML
    - 📑 自動生成目錄
    - 📈 瀏覽次數統計
    - 🔍 SEO 友好的 meta 資訊
    
    ## 🔍 包含內容
    - 文章標題和內容
    - HTML 渲染結果
    - 目錄結構
    - 封面圖片
    - SEO meta 標籤
    - 瀏覽統計
    
    ## 📊 自動記錄
    - 瀏覽次數自動增加
    - 訪客行為追蹤
    - 統計資料收集
    """,
    responses={
        200: {
            "description": "成功獲取文章內容",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "我的第一篇文章",
                        "content": "# 標題\n\n這是 Markdown 內容...",
                        "content_html": "<h1>標題</h1><p>這是 HTML 內容...</p>",
                        "toc": "[{\"level\": 1, \"text\": \"標題\", \"anchor\": \"#title\"}]",
                        "excerpt": "這是文章的摘要...",
                        "slug": "my-first-post",
                        "featured_image": "https://example.com/image.jpg",
                        "is_published": True,
                        "view_count": 124,
                        "meta_title": "我的第一篇文章",
                        "meta_description": "這是一篇關於...",
                        "meta_keywords": "部落格, 文章",
                        "created_at": "2024-01-15T10:30:00",
                        "updated_at": "2024-01-15T10:30:00"
                    }
                }
            }
        },
        404: {"description": "文章不存在"}
    }
)
def get_post(
    post_id: int, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    取得單一文章
    
    獲取指定 ID 的文章完整內容，同時記錄瀏覽統計。
    """
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


@router.get(
    "/slug/{slug}",
    response_model=PostResponse,
    summary="🔗 透過 Slug 獲取文章",
    description="""
    ## 🎯 功能描述
    透過 SEO 友好的 slug 獲取文章內容，常用於前端路由。
    
    ## 📋 功能特點
    - 🔗 SEO 友好的 URL
    - 📄 完整文章內容
    - 🎨 Markdown 渲染
    - 📈 瀏覽統計記錄
    
    ## 🔍 Slug 格式
    - 自動從標題生成
    - 包含連字符分隔
    - 移除特殊字符
    - 確保唯一性
    
    ## 📊 使用場景
    - 前端文章詳情頁
    - SEO 優化的 URL
    - 社群分享連結
    """,
    responses={
        200: {
            "description": "成功獲取文章內容",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "我的第一篇文章",
                        "slug": "my-first-post",
                        "content": "# 標題\n\n這是 Markdown 內容...",
                        "content_html": "<h1>標題</h1><p>這是 HTML 內容...</p>",
                        "excerpt": "這是文章的摘要...",
                        "view_count": 125
                    }
                }
            }
        },
        404: {"description": "文章不存在"}
    }
)
def get_post_by_slug(
    slug: str, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    透過 slug 取得文章
    
    使用 SEO 友好的 slug 獲取文章內容，同時記錄瀏覽統計。
    """
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


@router.post(
    "",
    response_model=PostResponse,
    summary="✍️ 建立新文章",
    description="""
    ## 🎯 功能描述
    建立新的部落格文章，支援 Markdown 格式和 SEO 優化。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 📝 Markdown 格式支援
    - 🔗 自動生成 SEO slug
    - 📄 自動摘要生成
    - 🎨 即時 HTML 渲染
    
    ## 🔍 驗證規則
    - 標題不可重複
    - 內容不可為空
    - Slug 自動生成且唯一
    
    ## 📊 自動處理
    - 從標題生成 slug
    - 從內容提取摘要
    - Markdown 轉 HTML
    - 生成目錄結構
    
    ## 🎯 使用場景
    - 管理後台文章發布
    - 內容創作工具
    - 批量內容匯入
    """,
    responses={
        200: {
            "description": "成功建立文章",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "title": "新文章標題",
                        "slug": "new-article-title",
                        "content": "# 新文章\n\n這是新文章的內容...",
                        "content_html": "<h1>新文章</h1><p>這是新文章的內容...</p>",
                        "excerpt": "這是新文章的摘要...",
                        "is_published": False,
                        "view_count": 0,
                        "created_at": "2024-01-15T10:30:00"
                    }
                }
            }
        },
        400: {"description": "文章標題已存在"},
        401: {"description": "需要管理員權限"},
        422: {"description": "驗證錯誤"}
    }
)
def create_post(
    post: PostCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    建立新文章
    
    建立新的部落格文章，包含 Markdown 處理和 SEO 優化。
    """
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


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="✏️ 更新文章",
    description="""
    ## 🎯 功能描述
    更新現有文章的內容、標題或其他屬性。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🔄 部分更新支援
    - 📝 Markdown 重新渲染
    - 🔗 Slug 自動更新
    - 📄 摘要自動生成
    
    ## 🔍 更新邏輯
    - 僅更新提供的欄位
    - 標題更新時重新生成 slug
    - 內容更新時重新生成摘要
    - 保留現有的瀏覽統計
    
    ## 📊 自動處理
    - 重新渲染 Markdown
    - 更新目錄結構
    - 重新生成摘要
    - 更新修改時間
    
    ## 🎯 使用場景
    - 內容編輯和修正
    - 發布狀態變更
    - SEO 優化調整
    """,
    responses={
        200: {
            "description": "成功更新文章",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "title": "更新後的標題",
                        "slug": "updated-title",
                        "content": "# 更新內容\n\n這是更新後的內容...",
                        "content_html": "<h1>更新內容</h1><p>這是更新後的內容...</p>",
                        "updated_at": "2024-01-15T14:30:00"
                    }
                }
            }
        },
        401: {"description": "需要管理員權限"},
        404: {"description": "文章不存在"},
        422: {"description": "驗證錯誤"}
    }
)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    更新文章
    
    更新指定文章的內容或屬性，支援部分更新。
    """
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


@router.delete(
    "/{post_id}",
    summary="🗑️ 刪除文章",
    description="""
    ## 🎯 功能描述
    永久刪除指定的文章，此操作不可逆轉。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🗑️ 永久刪除操作
    - 📊 自動清理統計資料
    - 🔗 移除相關聯資料
    
    ## ⚠️ 注意事項
    - 刪除操作不可逆轉
    - 會清理相關的瀏覽統計
    - 外部連結將失效
    - 建議先備份重要內容
    
    ## 🔍 安全措施
    - 需要管理員身份驗證
    - 確認文章存在性
    - 記錄刪除日誌
    
    ## 🎯 使用場景
    - 清理測試內容
    - 移除過期文章
    - 內容管理維護
    """,
    responses={
        200: {
            "description": "成功刪除文章",
            "content": {
                "application/json": {
                    "example": {
                        "message": "文章已刪除",
                        "deleted_id": 123
                    }
                }
            }
        },
        401: {"description": "需要管理員權限"},
        404: {"description": "文章不存在"}
    }
)
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    刪除文章
    
    永久刪除指定的文章及其相關資料。
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(post)
    db.commit()
    
    return {"message": "文章已刪除", "deleted_id": post_id} 