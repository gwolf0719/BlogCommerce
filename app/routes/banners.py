from fastapi import APIRouter, Depends, HTTPException, Query, Request, File, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from PIL import Image
import shutil

from app.database import get_db
from app.models.banner import Banner, BannerPosition
from app.schemas.banner import (
    BannerCreate, BannerUpdate, BannerResponse, BannerListResponse,
    BannerStatusToggle, BannerStats
)
from app.services.banner_service import BannerService
from app.auth import get_current_admin_user, get_current_user_optional
from app.models.user import User


router = APIRouter(prefix="/banners", tags=["廣告橫幅"])



@router.get("", response_model=BannerListResponse, summary="📋 取得廣告列表")
async def get_banners(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(10, ge=1, le=100, description="每頁項目數限制"),
):
    """
    取得廣告列表，支援多種篩選條件和分頁查詢。
    """
    banner_service = BannerService(db)
    
    # 從查詢參數解析篩選條件
    params = request.query_params
    position = params.get("position")
    is_active_str = params.get("is_active")
    search = params.get("search")

    is_active = None
    if is_active_str is not None:
        is_active = is_active_str.lower() in ['true', '1']

    total = banner_service.count_banners(
        position=position,
        is_active=is_active,
        search=search
    )
    
    banners = banner_service.get_banners(
        skip=skip,
        limit=limit,
        position=position,
        is_active=is_active,
        search=search
    )
    
    return BannerListResponse(items=banners, total=total)



@router.get(
    "/active/{position}",
    response_model=List[BannerResponse],
    summary="🎯 取得指定版位的啟用廣告",
    description="""
    ## 🎯 功能描述
    取得指定版位的所有啟用廣告，用於前端顯示。
    
    ## 📋 功能特點
    - 🔍 僅返回啟用且在有效期間內的廣告
    - 📈 按排序權重和建立時間排序
    - 🎯 支援三種版位：首頁、部落格列表、商品列表
    
    ## 🔍 版位說明
    - **home**: 首頁輪播廣告
    - **blog_list**: 部落格文章列表頁廣告
    - **product_list**: 商品列表頁廣告
    
    ## 🎯 使用場景
    - 前端頁面廣告顯示
    - 輪播組件資料獲取
    - 移動端廣告適配
    """,
    responses={
        200: {
            "description": "成功取得指定版位的啟用廣告",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "春季促銷活動",
                            "description": "全館商品8折起",
                            "link_url": "https://example.com/spring-sale",
                            "mobile_image": "/static/images/banner/mobile/spring-sale.jpg",
                            "desktop_image": "/static/images/banner/desktop/spring-sale.jpg",
                            "alt_text": "春季促銷活動",
                            "position": "home",
                            "start_date": "2024-01-01T00:00:00Z",
                            "end_date": "2024-01-31T23:59:59Z",
                            "is_active": True,
                            "sort_order": 10,
                            "click_count": 256,
                            "is_valid_period": True,
                            "is_displayable": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-02T12:00:00Z"
                        }
                    ]
                }
            }
        }
    }
)
async def get_active_banners_by_position(
    position: BannerPosition,
    db: Session = Depends(get_db)
):
    """
    取得指定版位的啟用廣告
    
    返回指定版位中所有啟用且在有效期間內的廣告。
    """
    banner_service = BannerService(db)
    banners = banner_service.get_active_banners_by_position(position)
    
    return [BannerResponse.model_validate(banner) for banner in banners]


@router.get(
    "/{banner_id}",
    response_model=BannerResponse,
    summary="🎯 取得單一廣告",
    description="""
    ## 🎯 功能描述
    透過廣告 ID 取得單一廣告的詳細資訊。
    
    ## 📋 功能特點
    - 🔍 取得完整的廣告資訊
    - 📊 包含統計資料
    - 🎯 包含狀態資訊
    
    ## 🎯 使用場景
    - 管理後台廣告編輯
    - 廣告詳細資訊查看
    - 廣告狀態檢查
    """,
    responses={
        200: {"description": "成功取得廣告資訊"},
        404: {"description": "廣告不存在"}
    }
)
async def get_banner(
    banner_id: int,
    db: Session = Depends(get_db)
):
    """
    取得單一廣告
    
    透過廣告 ID 取得廣告的詳細資訊。
    """
    banner_service = BannerService(db)
    banner = banner_service.get_banner_by_id(banner_id)
    
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="廣告不存在"
        )
    
    return BannerResponse.model_validate(banner)


@router.post(
    "",
    response_model=BannerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="✍️ 建立新廣告",
    description="""
    ## 🎯 功能描述
    建立新的輪播廣告，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🎨 支援手機和電腦版圖片
    - 🕒 支援時間範圍控制
    - 📍 支援版位指定
    - 📊 支援排序權重設定
    
    ## 🔍 驗證規則
    - 標題不可為空且長度限制200字元
    - 導向連結必須是有效的URL或相對路徑
    - 結束時間必須大於開始時間
    - 圖片路徑必須有效
    
    ## 📊 自動處理
    - 自動設定建立時間
    - 預設啟用狀態為true
    - 預設排序權重為0
    - 自動初始化點擊統計
    
    ## 🎯 使用場景
    - 管理後台廣告建立
    - 營銷活動廣告設定
    - 季節性促銷廣告
    """,
    responses={
        201: {
            "description": "成功建立廣告",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "title": "新年促銷活動",
                        "description": "全館商品7折起",
                        "link_url": "https://example.com/new-year-sale",
                        "mobile_image": "/static/images/banner/mobile/new-year.jpg",
                        "desktop_image": "/static/images/banner/desktop/new-year.jpg",
                        "alt_text": "新年促銷活動",
                        "position": "home",
                        "start_date": "2024-01-01T00:00:00Z",
                        "end_date": "2024-01-31T23:59:59Z",
                        "is_active": True,
                        "sort_order": 10,
                        "click_count": 0,
                        "is_valid_period": True,
                        "is_displayable": True,
                        "created_at": "2024-01-01T00:00:00Z",
                                                    "updated_at": None
                    }
                }
            }
        },
        400: {"description": "廣告資料驗證失敗"},
        401: {"description": "需要管理員權限"},
        422: {"description": "驗證錯誤"}
    }
)
async def create_banner(
    banner_data: BannerCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    建立新廣告
    
    建立新的輪播廣告，需要管理員權限。
    """
    banner_service = BannerService(db)
    banner = banner_service.create_banner(banner_data)
    
    return BannerResponse.model_validate(banner)


@router.put(
    "/{banner_id}",
    response_model=BannerResponse,
    summary="✏️ 更新廣告",
    description="""
    ## 🎯 功能描述
    更新現有廣告的資訊，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🎨 支援部分欄位更新
    - 🕒 支援時間範圍調整
    - 📍 支援版位變更
    - 📊 支援排序權重調整
    
    ## 🔍 驗證規則
    - 更新欄位必須符合格式要求
    - 時間範圍必須合理
    - 連結必須有效
    
    ## 📊 自動處理
    - 自動更新修改時間
    - 保留原有點擊統計
    - 重新計算可顯示狀態
    
    ## 🎯 使用場景
    - 管理後台廣告編輯
    - 廣告內容調整
    - 時間範圍修改
    """,
    responses={
        200: {"description": "成功更新廣告"},
        400: {"description": "廣告資料驗證失敗"},
        401: {"description": "需要管理員權限"},
        404: {"description": "廣告不存在"},
        422: {"description": "驗證錯誤"}
    }
)
async def update_banner(
    banner_id: int,
    banner_data: BannerUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新廣告
    
    更新現有廣告的資訊，需要管理員權限。
    """
    banner_service = BannerService(db)
    banner = banner_service.update_banner(banner_id, banner_data)
    
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="廣告不存在"
        )
    
    return BannerResponse.model_validate(banner)


@router.delete(
    "/{banner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="🗑️ 刪除廣告",
    description="""
    ## 🎯 功能描述
    刪除指定的廣告，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🗑️ 永久刪除廣告
    - 📊 清除相關統計
    
    ## ⚠️ 注意事項
    - 刪除操作不可逆
    - 建議先停用廣告再刪除
    - 會清除所有相關資料
    
    ## 🎯 使用場景
    - 管理後台廣告管理
    - 過期廣告清理
    - 錯誤廣告移除
    """,
    responses={
        204: {"description": "成功刪除廣告"},
        401: {"description": "需要管理員權限"},
        404: {"description": "廣告不存在"}
    }
)
async def delete_banner(
    banner_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    刪除廣告
    
    永久刪除指定的廣告，需要管理員權限。
    """
    banner_service = BannerService(db)
    success = banner_service.delete_banner(banner_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="廣告不存在"
        )


@router.post(
    "/{banner_id}/toggle",
    response_model=BannerResponse,
    summary="🔄 切換廣告狀態",
    description="""
    ## 🎯 功能描述
    切換廣告的啟用狀態，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🔄 一鍵切換啟用/停用
    - 📊 即時生效
    
    ## 🎯 使用場景
    - 快速啟用/停用廣告
    - 緊急廣告控制
    - 批量狀態管理
    """,
    responses={
        200: {"description": "成功切換廣告狀態"},
        401: {"description": "需要管理員權限"},
        404: {"description": "廣告不存在"}
    }
)
async def toggle_banner_status(
    banner_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    切換廣告狀態
    
    切換廣告的啟用狀態，需要管理員權限。
    """
    banner_service = BannerService(db)
    banner = banner_service.toggle_banner_status(banner_id)
    
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="廣告不存在"
        )
    
    return BannerResponse.model_validate(banner)


@router.post(
    "/{banner_id}/click",
    summary="📊 記錄廣告點擊",
    description="""
    ## 🎯 功能描述
    記錄廣告點擊事件，用於統計分析。
    
    ## 📋 功能特點
    - 📊 自動增加點擊次數
    - 🔍 不需要認證
    - 📈 即時統計
    
    ## 🎯 使用場景
    - 前端廣告點擊追蹤
    - 統計分析資料收集
    - 廣告效果評估
    """,
    responses={
        200: {"description": "成功記錄廣告點擊"},
        404: {"description": "廣告不存在"}
    }
)
async def track_banner_click(
    banner_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    記錄廣告點擊
    
    記錄廣告點擊事件，用於統計分析。
    """
    banner_service = BannerService(db)
    success = banner_service.track_banner_click(banner_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="廣告不存在"
        )
    
    return {"message": "點擊記錄成功"}


@router.get(
    "/stats/overview",
    response_model=BannerStats,
    summary="📊 取得廣告統計",
    description="""
    ## 🎯 功能描述
    取得廣告系統的統計資料，需要管理員權限。
    
    ## 📋 統計內容
    - 📊 總廣告數
    - 📈 啟用廣告數
    - 📉 過期廣告數
    - 🖱️ 總點擊次數
    - 📍 各版位統計
    
    ## 🎯 使用場景
    - 管理後台統計面板
    - 廣告效果分析
    - 營銷決策支援
    """,
    responses={
        200: {"description": "成功取得廣告統計"},
        401: {"description": "需要管理員權限"}
    }
)
async def get_banner_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得廣告統計
    
    取得廣告系統的統計資料，需要管理員權限。
    """
    banner_service = BannerService(db)
    stats = banner_service.get_banner_stats()
    
    return stats


@router.post(
    "/upload",
    summary="📸 上傳廣告圖片",
    description="""
    ## 🎯 功能描述
    上傳廣告圖片，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 📸 支援多種圖片格式
    - 🎨 自動壓縮優化
    - 📱 響應式適配
    
    ## 🔍 檔案限制
    - 檔案大小：最大 5MB
    - 支援格式：JPG、PNG、GIF
    - 建議尺寸：桌面版1920x400、手機版750x300
    
    ## 🎯 使用場景
    - 廣告圖片上傳
    - 圖片替換更新
    - 批量圖片處理
    """,
    responses={
        200: {"description": "成功上傳圖片"},
        400: {"description": "圖片格式不支援或檔案過大"},
        401: {"description": "需要管理員權限"}
    }
)
async def upload_banner_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user)
):
    """
    上傳廣告圖片
    
    上傳廣告圖片，需要管理員權限。
    """
    # 檢查檔案類型
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支援的圖片格式，僅支援 JPG、PNG、GIF"
        )
    
    # 檢查檔案大小 (5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="圖片檔案過大，最大允許 5MB"
        )
    
    try:
        # 建立上傳目錄
        upload_dir = "app/static/images/banner"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一檔名
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="檔案名稱不能為空"
            )
        
        file_extension = file.filename.split(".")[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 儲存檔案
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 返回檔案路徑
        return {
            "message": "圖片上傳成功",
            "file_path": f"/static/images/banner/{unique_filename}",
            "filename": unique_filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"圖片上傳失敗: {str(e)}"
        ) 