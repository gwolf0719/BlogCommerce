from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.view_tracking_service import ViewTrackingService
from app.auth import get_current_user_optional
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List, Dict
from urllib.parse import urlparse, parse_qs


router = APIRouter(prefix="/api/views", tags=["view_tracking"])


class ViewTrackingRequest(BaseModel):
    """
    瀏覽追蹤請求 Schema
    
    用於記錄用戶瀏覽行為的請求結構，支援 UTM 參數和停留時間追蹤。
    """
    content_type: str  # 'post' 或 'product'
    content_id: int
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    duration: Optional[int] = None  # 停留時間（秒）
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "product",
                "content_id": 123,
                "referrer": "https://google.com",
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "spring_sale",
                "duration": 45
            }
        }


@router.post(
    "/track",
    summary="📊 記錄瀏覽追蹤",
    description="""
    ## 🎯 功能描述
    記錄用戶的瀏覽行為，包括頁面訪問、停留時間和來源追蹤。
    
    ## 📋 功能特點
    - 📈 支援多種內容類型（文章、商品）
    - 🔗 UTM 參數自動解析
    - ⏱️ 停留時間記錄
    - 🌐 來源頁面追蹤
    - 📱 設備和瀏覽器資訊
    
    ## 🔍 追蹤項目
    - 內容類型和 ID
    - 用戶會話資訊
    - IP 地址和用戶代理
    - UTM 行銷參數
    - 頁面停留時間
    
    ## 📊 用途
    - 網站流量分析
    - 內容熱門度統計
    - 行銷效果追蹤
    - 用戶行為分析
    """,
    responses={
        200: {
            "description": "成功記錄瀏覽追蹤",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "view_id": 789
                    }
                }
            }
        },
        400: {"description": "無效的內容類型"}
    }
)
def track_view(
    request: Request,
    tracking_data: ViewTrackingRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    記錄瀏覽行為
    
    追蹤用戶的頁面訪問行為並記錄相關統計資料。
    """
    
    # 驗證內容類型
    if tracking_data.content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    # 獲取客戶端信息
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    session_id = request.session.get("session_id")
    
    # 如果沒有 session_id，創建一個
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
    
    # 解析 UTM 參數（如果在 referrer 中）
    if tracking_data.referrer and not tracking_data.utm_source:
        parsed_url = urlparse(tracking_data.referrer)
        query_params = parse_qs(parsed_url.query)
        tracking_data.utm_source = query_params.get('utm_source', [None])[0]
        tracking_data.utm_medium = query_params.get('utm_medium', [None])[0]
        tracking_data.utm_campaign = query_params.get('utm_campaign', [None])[0]
    
    # 記錄瀏覽
    view_log = ViewTrackingService.record_view(
        db=db,
        content_type=tracking_data.content_type,
        content_id=tracking_data.content_id,
        user_id=current_user.id if current_user else None,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=tracking_data.referrer,
        utm_source=tracking_data.utm_source,
        utm_medium=tracking_data.utm_medium,
        utm_campaign=tracking_data.utm_campaign
    )
    
    return {"success": True, "view_id": view_log.id}


@router.get(
    "/popular/{content_type}",
    summary="🔥 獲取熱門內容",
    description="""
    ## 🎯 功能描述
    獲取指定內容類型的熱門項目，基於瀏覽次數統計。
    
    ## 📋 功能特點
    - 📊 基於瀏覽次數排序
    - 📅 可自訂時間範圍
    - 🔢 可設定回傳數量
    - 🎯 支援多種內容類型
    
    ## 🔍 統計邏輯
    - 統計指定天數內的瀏覽次數
    - 按瀏覽次數降序排列
    - 支援文章和商品類型
    - 去重複計算
    
    ## 📊 回應格式
    返回熱門項目列表，包含瀏覽次數和內容資訊。
    """,
    responses={
        200: {
            "description": "成功獲取熱門內容",
            "content": {
                "application/json": {
                    "example": {
                        "popular_items": [
                            {
                                "content_id": 123,
                                "content_type": "product",
                                "view_count": 456,
                                "title": "熱門商品",
                                "url": "/product/123"
                            }
                        ]
                    }
                }
            }
        },
        400: {"description": "無效的內容類型"}
    }
)
def get_popular_content(
    content_type: str,
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    獲取熱門內容
    
    根據瀏覽次數統計獲取指定時間範圍內的熱門內容。
    """
    
    if content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    popular_items = ViewTrackingService.get_popular_content(
        db=db,
        content_type=content_type,
        days=days,
        limit=limit
    )
    
    return {"popular_items": popular_items}


@router.get(
    "/trending/{content_type}",
    summary="📈 獲取趨勢內容",
    description="""
    ## 🎯 功能描述
    獲取指定內容類型的趨勢項目，基於短時間內的瀏覽增長。
    
    ## 📋 功能特點
    - 📊 基於瀏覽增長率排序
    - ⏰ 短時間範圍分析
    - 🔥 即時趨勢發現
    - 📈 增長率計算
    
    ## 🔍 統計邏輯
    - 分析指定小時數內的瀏覽趨勢
    - 計算瀏覽增長率
    - 識別快速增長的內容
    - 按趨勢強度排序
    
    ## 📊 回應格式
    返回趨勢項目列表，包含增長率和內容資訊。
    """,
    responses={
        200: {
            "description": "成功獲取趨勢內容",
            "content": {
                "application/json": {
                    "example": {
                        "trending_items": [
                            {
                                "content_id": 456,
                                "content_type": "post",
                                "view_count": 123,
                                "growth_rate": 85.2,
                                "title": "趨勢文章",
                                "url": "/blog/456"
                            }
                        ]
                    }
                }
            }
        },
        400: {"description": "無效的內容類型"}
    }
)
def get_trending_content(
    content_type: str,
    hours: int = 24,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    獲取趨勢內容
    
    分析短時間內瀏覽量快速增長的內容。
    """
    
    if content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    trending_items = ViewTrackingService.get_trending_content(
        db=db,
        content_type=content_type,
        hours=hours,
        limit=limit
    )
    
    return {"trending_items": trending_items}


@router.get(
    "/stats/{content_type}/{content_id}",
    summary="📊 獲取內容統計",
    description="""
    ## 🎯 功能描述
    獲取指定內容的詳細瀏覽統計資料。
    
    ## 📋 功能特點
    - 📊 詳細統計數據
    - 📅 時間範圍分析
    - 🔍 單一內容深度分析
    - 📈 趨勢變化追蹤
    
    ## 🔍 統計項目
    - 總瀏覽次數
    - 獨立訪客數
    - 瀏覽時間分佈
    - 來源統計
    - 時間趨勢圖表
    
    ## 📊 回應格式
    返回完整的統計資料，包含各種分析維度。
    """,
    responses={
        200: {
            "description": "成功獲取內容統計",
            "content": {
                "application/json": {
                    "example": {
                        "stats": {
                            "total_views": 1234,
                            "unique_visitors": 789,
                            "avg_duration": 123.5,
                            "bounce_rate": 45.2,
                            "top_referrers": [
                                {"domain": "google.com", "count": 456},
                                {"domain": "facebook.com", "count": 234}
                            ],
                            "daily_views": [
                                {"date": "2024-01-01", "views": 50},
                                {"date": "2024-01-02", "views": 75}
                            ]
                        }
                    }
                }
            }
        },
        400: {"description": "無效的內容類型"}
    }
)
def get_content_stats(
    content_type: str,
    content_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    獲取內容瀏覽統計
    
    提供特定內容的詳細瀏覽分析資料。
    """
    
    if content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    stats = ViewTrackingService.get_content_view_stats(
        db=db,
        content_type=content_type,
        content_id=content_id,
        days=days
    )
    
    return {"stats": stats}


@router.get(
    "/history",
    summary="📚 獲取瀏覽歷史",
    description="""
    ## 🎯 功能描述
    獲取當前用戶的瀏覽歷史記錄。
    
    ## 📋 功能特點
    - 🔐 需要用戶認證
    - 📅 時間順序排列
    - 🔍 內容類型篩選
    - 📊 瀏覽詳情記錄
    
    ## 🔍 記錄項目
    - 瀏覽時間
    - 內容類型和 ID
    - 停留時間
    - 來源頁面
    - 瀏覽序列
    
    ## 📊 回應格式
    返回用戶的瀏覽歷史陣列，按時間降序排列。
    """,
    responses={
        200: {
            "description": "成功獲取瀏覽歷史",
            "content": {
                "application/json": {
                    "example": {
                        "history": [
                            {
                                "id": 789,
                                "content_type": "product",
                                "content_id": 123,
                                "viewed_at": "2024-01-15T14:30:00",
                                "duration": 45,
                                "referrer": "https://google.com"
                            }
                        ]
                    }
                }
            }
        },
        400: {"description": "無效的內容類型"},
        401: {"description": "需要用戶認證"}
    }
)
def get_user_view_history(
    content_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    獲取用戶瀏覽歷史
    
    返回用戶的個人瀏覽記錄，支援內容類型篩選。
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if content_type and content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    history = ViewTrackingService.get_user_view_history(
        db=db,
        user_id=current_user.id,
        content_type=content_type,
        limit=limit
    )
    
    # 轉換為可序列化的格式
    history_data = []
    for view in history:
        history_data.append({
            "id": view.id,
            "content_type": view.content_type,
            "content_id": view.content_id,
            "viewed_at": view.viewed_at.isoformat(),
            "duration": view.duration,
            "referrer": view.referrer
        })
    
    return {"history": history_data} 