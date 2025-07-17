from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models.discount_code import PromoCode
from app.models.discount_usage import PromoUsage
from app.schemas.discount_code import (
    PromoCodeCreate, PromoCodeUpdate, PromoCodeResponse, 
    PromoCodeListResponse, PromoCodeValidateRequest, 
    PromoCodeValidateResponse, PromoCodeUsageResponse,
    PromoCodeUsageListResponse, PromoCodeStatsResponse,
    PromoTypeEnum
)
from app.services.discount_service import PromoService
from app.auth import get_current_admin_user, get_current_user_optional
from app.models.user import User


router = APIRouter(prefix="/discount-codes", tags=["折扣碼管理"])



@router.get(
    "",
    response_model=List[PromoCodeListResponse],
    summary="📋 取得推薦碼列表",
    description="""
    ## 🎯 功能描述
    取得推薦碼列表，支援多種篩選條件和分頁查詢。
    
    ## 📋 功能特點
    - 🔍 支援啟用狀態篩選
    - 📄 支援分頁查詢
    - 📈 按建立時間排序
    - 🎯 管理員權限
    
    ## 🔍 查詢參數
    - **is_active**: 啟用狀態篩選
    - **skip**: 跳過的項目數（分頁）
    - **limit**: 每頁項目數限制
    
    ## 🎯 使用場景
    - 管理後台推薦碼管理
    - 推薦碼狀態監控
    - 行銷活動管理
    """,
    responses={
        200: {
            "description": "成功取得推薦碼列表",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "code": "SPRING2024",
                            "name": "春季促銷活動",
                            "source": "Facebook",
                            "promo_type": "percentage",
                            "promo_value": 20.00,
                            "start_date": "2024-03-01T00:00:00Z",
                            "end_date": "2024-03-31T23:59:59Z",
                            "usage_limit": 1000,
                            "used_count": 256,
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    ]
                }
            }
        }
    }
)
async def get_promo_codes(
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(100, ge=1, le=100, description="每頁項目數限制"),
    is_active: Optional[bool] = Query(None, description="啟用狀態篩選"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得推薦碼列表
    
    支援多種篩選條件的推薦碼列表查詢，需要管理員權限。
    """
    promo_service = PromoService(db)
    promo_codes = promo_service.get_promo_codes(
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    
    return [PromoCodeListResponse.model_validate(code) for code in promo_codes]


@router.post(
    "/validate",
    response_model=PromoCodeValidateResponse,
    summary="🔍 驗證推薦碼",
    description="""
    ## 🎯 功能描述
    驗證推薦碼是否有效，並計算推薦金額。
    
    ## 📋 功能特點
    - 🔍 檢查推薦碼有效性
    - 💰 計算推薦金額
    - 🕒 檢查時間範圍
    - 📊 檢查使用限制
    - 🎯 檢查最小訂單金額
    
    ## 🔍 驗證項目
    - 推薦碼是否存在
    - 是否在有效期間內
    - 是否已啟用
    - 使用次數是否已達上限
    - 訂單金額是否符合要求
    
    ## 🎯 使用場景
    - 購物車推薦碼驗證
    - 結帳前推薦計算
    - 前端即時驗證
    """,
    responses={
        200: {"description": "成功驗證推薦碼"},
        400: {"description": "驗證請求參數錯誤"}
    }
)
async def validate_promo_code(
    validate_data: PromoCodeValidateRequest,
    db: Session = Depends(get_db)
):
    """
    驗證推薦碼
    
    驗證推薦碼是否有效並計算推薦金額。
    """
    promo_service = PromoService(db)
    
    result = promo_service.validate_promo_code(
        validate_data.code,
        validate_data.order_amount
    )
    
    return PromoCodeValidateResponse(
        is_valid=result["is_valid"],
        promo_amount=result["promo_amount"],
        message=result["message"],
        promo_code=PromoCodeResponse.model_validate(result["promo_code"]) if result.get("promo_code") else None
    )


@router.get(
    "/stats",
    response_model=PromoCodeStatsResponse,
    summary="📊 取得推薦碼統計",
    description="""
    ## 🎯 功能描述
    取得推薦碼系統的統計資料，需要管理員權限。
    
    ## 📋 統計內容
    - 📊 總推薦碼數
    - 📈 啟用推薦碼數
    - 📉 總使用次數
    - 💰 總推薦金額
    - 🏆 最熱門推薦碼
    
    ## 🎯 使用場景
    - 管理後台統計面板
    - 營銷效果分析
    - 業務決策支援
    """,
    responses={
        200: {"description": "成功取得推薦碼統計"},
        401: {"description": "需要管理員權限"}
    }
)
async def get_promo_code_stats_simple(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得推薦碼統計（簡化版）
    
    取得推薦碼系統的統計資料，需要管理員權限。
    """
    promo_service = PromoService(db)
    stats = promo_service.get_promo_stats()
    
    return PromoCodeStatsResponse(**stats)


@router.get(
    "/stats/overview",
    response_model=PromoCodeStatsResponse,
    summary="📊 取得推薦碼統計",
    description="""
    ## 🎯 功能描述
    取得推薦碼系統的統計資料，需要管理員權限。
    
    ## 📋 統計內容
    - 📊 總推薦碼數
    - 📈 啟用推薦碼數
    - 📉 總使用次數
    - 💰 總推薦金額
    - 🏆 最熱門推薦碼
    
    ## 🎯 使用場景
    - 管理後台統計面板
    - 營銷效果分析
    - 業務決策支援
    """,
    responses={
        200: {"description": "成功取得推薦碼統計"},
        401: {"description": "需要管理員權限"}
    }
)
async def get_promo_code_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得推薦碼統計
    
    取得推薦碼系統的統計資料，需要管理員權限。
    """
    promo_service = PromoService(db)
    stats = promo_service.get_promo_stats()
    
    return PromoCodeStatsResponse(**stats)


@router.get(
    "/{promo_code_id}/usage",
    response_model=List[PromoCodeUsageListResponse],
    summary="📊 取得推薦碼使用記錄",
    description="""
    ## 🎯 功能描述
    取得指定推薦碼的使用記錄，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 📊 完整使用記錄
    - 📄 支援分頁查詢
    - 🕒 按使用時間排序
    
    ## 🎯 使用場景
    - 推薦碼效果分析
    - 使用者行為追蹤
    - 營銷活動評估
    """,
    responses={
        200: {"description": "成功取得使用記錄"},
        401: {"description": "需要管理員權限"},
        404: {"description": "推薦碼不存在"}
    }
)
async def get_promo_code_usage(
    promo_code_id: int,
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(100, ge=1, le=100, description="每頁項目數限制"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得推薦碼使用記錄
    
    取得指定推薦碼的使用記錄，需要管理員權限。
    """
    promo_service = PromoService(db)
    
    # 檢查推薦碼是否存在
    promo_code = promo_service.get_promo_code_by_id(promo_code_id)
    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推薦碼不存在"
        )
    
    usage_records = promo_service.get_promo_usage_history(
        promo_code_id=promo_code_id,
        skip=skip,
        limit=limit
    )
    
    # 組合回應資料
    response_data = []
    for usage in usage_records:
        response_data.append({
            "id": usage.id,
            "promo_code_id": usage.promo_code_id,
            "promo_code": promo_code.code,
            "user_id": usage.user_id,
            "order_id": usage.order_id,
            "promo_amount": usage.promo_amount,
            "original_amount": usage.original_amount,
            "final_amount": usage.final_amount,
            "used_at": usage.used_at,
            "created_at": usage.created_at,
            "updated_at": usage.updated_at
        })
    
    return response_data


@router.get(
    "/{promo_code_id}",
    response_model=PromoCodeResponse,
    summary="🎯 取得單一推薦碼",
    description="""
    ## 🎯 功能描述
    透過推薦碼 ID 取得單一推薦碼的詳細資訊。
    
    ## 📋 功能特點
    - 🔍 取得完整的推薦碼資訊
    - 📊 包含使用統計
    - 🎯 包含狀態資訊
    - 🔐 需要管理員權限
    
    ## 🎯 使用場景
    - 管理後台推薦碼編輯
    - 推薦碼詳細資訊查看
    - 推薦碼效果分析
    """,
    responses={
        200: {"description": "成功取得推薦碼資訊"},
        404: {"description": "推薦碼不存在"}
    }
)
async def get_promo_code(
    promo_code_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得單一推薦碼
    
    根據 ID 取得推薦碼的詳細資訊，需要管理員權限。
    """
    promo_service = PromoService(db)
    promo_code = promo_service.get_promo_code_by_id(promo_code_id)
    
    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推薦碼不存在"
        )
    
    return PromoCodeResponse.model_validate(promo_code)


@router.post(
    "",
    response_model=PromoCodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="✍️ 建立新推薦碼",
    description="""
    ## 🎯 功能描述
    建立新的推薦碼，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🎯 支援多種推薦類型
    - 🕒 支援時間範圍控制
    - 📊 支援使用次數限制
    - 💰 支援最小訂單金額設定
    
    ## 🔍 驗證規則
    - 推薦碼必須唯一
    - 結束時間必須大於開始時間
    - 推薦值必須合理
    - 百分比推薦不可超過100%
    
    ## 📊 自動處理
    - 自動轉換為大寫
    - 自動設定建立時間
    - 初始化使用次數為0
    
    ## 🎯 使用場景
    - 管理後台推薦碼建立
    - 營銷活動推薦設定
    - 會員專屬優惠
    """,
    responses={
        201: {"description": "成功建立推薦碼"},
        400: {"description": "推薦碼資料驗證失敗或已存在"},
        401: {"description": "需要管理員權限"},
        422: {"description": "驗證錯誤"}
    }
)
async def create_promo_code(
    promo_data: PromoCodeCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    建立新推薦碼
    
    建立新的推薦碼，需要管理員權限。
    """
    promo_service = PromoService(db)
    
    try:
        promo_code = promo_service.create_promo_code(promo_data)
        return PromoCodeResponse.model_validate(promo_code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{promo_code_id}",
    response_model=PromoCodeResponse,
    summary="✏️ 更新推薦碼",
    description="""
    ## 🎯 功能描述
    更新現有推薦碼的資訊，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🎯 支援部分欄位更新
    - 🕒 支援時間範圍調整
    - 📊 支援使用限制修改
    
    ## 🔍 驗證規則
    - 更新欄位必須符合格式要求
    - 時間範圍必須合理
    - 推薦值必須有效
    
    ## 📊 自動處理
    - 自動更新修改時間
    - 保留原有使用統計
    
    ## 🎯 使用場景
    - 管理後台推薦碼編輯
    - 推薦碼內容調整
    - 時間範圍修改
    """,
    responses={
        200: {"description": "成功更新推薦碼"},
        400: {"description": "推薦碼資料驗證失敗"},
        401: {"description": "需要管理員權限"},
        404: {"description": "推薦碼不存在"},
        422: {"description": "驗證錯誤"}
    }
)
async def update_promo_code(
    promo_code_id: int,
    promo_data: PromoCodeUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新推薦碼
    
    更新現有推薦碼的資訊，需要管理員權限。
    """
    promo_service = PromoService(db)
    
    try:
        promo_code = promo_service.update_promo_code(promo_code_id, promo_data)
        if not promo_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="推薦碼不存在"
            )
        return PromoCodeResponse.model_validate(promo_code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{promo_code_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="🗑️ 刪除推薦碼",
    description="""
    ## 🎯 功能描述
    刪除指定的推薦碼，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🗑️ 永久刪除推薦碼
    - 🛡️ 已使用的推薦碼無法刪除
    
    ## ⚠️ 注意事項
    - 刪除操作不可逆
    - 已有使用記錄的推薦碼無法刪除
    - 建議先停用推薦碼再刪除
    
    ## 🎯 使用場景
    - 管理後台推薦碼管理
    - 錯誤推薦碼清理
    - 測試推薦碼移除
    """,
    responses={
        204: {"description": "成功刪除推薦碼"},
        400: {"description": "推薦碼已被使用，無法刪除"},
        401: {"description": "需要管理員權限"},
        404: {"description": "推薦碼不存在"}
    }
)
async def delete_promo_code(
    promo_code_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    刪除推薦碼
    
    刪除指定的推薦碼，需要管理員權限。
    """
    promo_service = PromoService(db)
    
    try:
        success = promo_service.delete_promo_code(promo_code_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="推薦碼不存在"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# 向後相容的路由別名
discount_router = router 