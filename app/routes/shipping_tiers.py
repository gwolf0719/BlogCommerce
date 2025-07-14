from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models.shipping_tier import ShippingTier
from app.schemas.shipping_tier import (
    ShippingTierCreate, ShippingTierUpdate, ShippingTierResponse, 
    ShippingTierListResponse, ShippingTierStatusToggle, ShippingTierStats,
    ShippingCalculationRequest, ShippingCalculationResponse
)
from app.services.shipping_tier_service import ShippingTierService
from app.auth import get_current_admin_user, get_current_user_optional
from app.models.user import User


router = APIRouter(prefix="/shipping-tiers", tags=["運費級距"])



@router.get(
    "",
    response_model=List[ShippingTierListResponse],
    summary="📋 取得運費級距列表",
    description="""
    ## 🎯 功能描述
    取得運費級距列表，支援多種篩選條件和分頁查詢。
    
    ## 📋 功能特點
    - 🔍 支援啟用狀態篩選
    - 📊 支援金額排序或權重排序
    - 📄 支援分頁查詢
    - 📈 靈活的排序方式
    
    ## 🔍 查詢參數
    - **is_active**: 啟用狀態篩選
    - **sort_by_amount**: 是否按金額排序（預設按最低金額升序）
    - **skip**: 跳過的項目數（分頁）
    - **limit**: 每頁項目數限制
    
    ## 📊 排序規則
    - sort_by_amount=true：按最低金額升序，然後按排序權重降序
    - sort_by_amount=false：按排序權重降序，然後按建立時間降序
    
    ## 🎯 使用場景
    - 管理後台運費級距管理
    - 運費計算邏輯查看
    - 級距設定檢查
    """,
    responses={
        200: {
            "description": "成功取得運費級距列表",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "免運費級距",
                            "min_amount": "1000.00",
                            "max_amount": None,
                            "shipping_fee": "0.00",
                            "free_shipping": True,
                            "is_active": True,
                            "sort_order": 10,
                            "is_unlimited_max": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-02T12:00:00Z"
                        }
                    ]
                }
            }
        }
    }
)
async def get_shipping_tiers(
    skip: int = Query(0, ge=0, description="跳過的項目數"),
    limit: int = Query(100, ge=1, le=100, description="每頁項目數限制"),
    is_active: Optional[bool] = Query(None, description="啟用狀態篩選"),
    sort_by_amount: bool = Query(True, description="是否按金額排序"),
    db: Session = Depends(get_db)
):
    """
    取得運費級距列表
    
    支援多種篩選條件的運費級距列表查詢。
    """
    shipping_service = ShippingTierService(db)
    tiers = shipping_service.get_shipping_tiers(
        skip=skip,
        limit=limit,
        is_active=is_active,
        sort_by_amount=sort_by_amount
    )
    
    return [ShippingTierListResponse.model_validate(tier) for tier in tiers]


@router.get(
    "/active",
    response_model=List[ShippingTierResponse],
    summary="🎯 取得啟用的運費級距",
    description="""
    ## 🎯 功能描述
    取得所有啟用的運費級距，按金額排序，用於運費計算。
    
    ## 📋 功能特點
    - 🔍 僅返回啟用的級距
    - 📈 按最低金額升序排序
    - 🎯 用於前端運費顯示和計算
    
    ## 🎯 使用場景
    - 前端運費說明顯示
    - 運費計算邏輯獲取
    - 購物車運費預覽
    """,
    responses={
        200: {
            "description": "成功取得啟用的運費級距",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "基本運費",
                            "min_amount": "0.00",
                            "max_amount": "500.00",
                            "shipping_fee": "60.00",
                            "free_shipping": False,
                            "is_active": True,
                            "sort_order": 0,
                            "is_unlimited_max": False,
                            "created_at": "2024-01-01T00:00:00Z"
                        },
                        {
                            "id": 2,
                            "name": "免運費級距",
                            "min_amount": "1000.00",
                            "max_amount": None,
                            "shipping_fee": "0.00",
                            "free_shipping": True,
                            "is_active": True,
                            "sort_order": 10,
                            "is_unlimited_max": True,
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    ]
                }
            }
        }
    }
)
async def get_active_shipping_tiers(
    db: Session = Depends(get_db)
):
    """
    取得啟用的運費級距
    
    返回所有啟用的運費級距，按金額排序。
    """
    shipping_service = ShippingTierService(db)
    tiers = shipping_service.get_active_shipping_tiers()
    
    return [ShippingTierResponse.model_validate(tier) for tier in tiers]


@router.get(
    "/{tier_id}",
    response_model=ShippingTierResponse,
    summary="🎯 取得單一運費級距",
    description="""
    ## 🎯 功能描述
    透過運費級距 ID 取得單一級距的詳細資訊。
    
    ## 📋 功能特點
    - 🔍 取得完整的級距資訊
    - 📊 包含計算屬性
    - 🎯 包含狀態資訊
    
    ## 🎯 使用場景
    - 管理後台級距編輯
    - 級距詳細資訊查看
    - 級距設定檢查
    """,
    responses={
        200: {"description": "成功取得運費級距資訊"},
        404: {"description": "運費級距不存在"}
    }
)
async def get_shipping_tier(
    tier_id: int,
    db: Session = Depends(get_db)
):
    """
    取得單一運費級距
    
    透過 ID 取得運費級距的詳細資訊。
    """
    shipping_service = ShippingTierService(db)
    tier = shipping_service.get_shipping_tier_by_id(tier_id)
    
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="運費級距不存在"
        )
    
    return ShippingTierResponse.model_validate(tier)


@router.post(
    "",
    response_model=ShippingTierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="✍️ 建立新運費級距",
    description="""
    ## 🎯 功能描述
    建立新的運費級距，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 💰 支援金額範圍設定
    - 🚚 支援運費金額或免運設定
    - 🔍 自動檢查級距衝突
    - 📊 支援排序權重設定
    
    ## 🔍 驗證規則
    - 級距名稱不可為空
    - 最低金額必須 >= 0
    - 最高金額必須 > 最低金額（如果設定）
    - 免運費時運費金額應為 0
    - 不可與現有級距範圍衝突
    
    ## 📊 自動處理
    - 自動設定建立時間
    - 預設啟用狀態為 true
    - 預設排序權重為 0
    - 自動檢查級距衝突
    
    ## 🎯 使用場景
    - 管理後台運費設定
    - 營銷活動運費調整
    - 季節性運費政策
    """,
    responses={
        201: {
            "description": "成功建立運費級距",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "name": "滿千免運",
                        "description": "訂單金額滿1000元免運費",
                        "min_amount": "1000.00",
                        "max_amount": None,
                        "shipping_fee": "0.00",
                        "free_shipping": True,
                        "is_active": True,
                        "sort_order": 10,
                        "is_unlimited_max": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": None
                    }
                }
            }
        },
        400: {"description": "運費級距資料驗證失敗或存在衝突"},
        401: {"description": "需要管理員權限"},
        422: {"description": "驗證錯誤"}
    }
)
async def create_shipping_tier(
    tier_data: ShippingTierCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    建立新運費級距
    
    建立新的運費級距設定。
    """
    shipping_service = ShippingTierService(db)
    tier = shipping_service.create_shipping_tier(tier_data)
    
    return ShippingTierResponse.model_validate(tier)


@router.put(
    "/{tier_id}",
    response_model=ShippingTierResponse,
    summary="✏️ 更新運費級距",
    description="""
    ## 🎯 功能描述
    更新現有運費級距的資訊，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 💰 支援部分欄位更新
    - 🔍 自動檢查級距衝突（排除自己）
    - 📊 支援狀態調整
    
    ## 🔍 驗證規則
    - 更新欄位必須符合格式要求
    - 金額範圍必須合理
    - 不可與其他級距衝突
    
    ## 📊 自動處理
    - 自動更新修改時間
    - 重新檢查級距衝突
    - 保留原有資料
    
    ## 🎯 使用場景
    - 管理後台級距編輯
    - 運費政策調整
    - 金額範圍修改
    """,
    responses={
        200: {"description": "成功更新運費級距"},
        400: {"description": "運費級距資料驗證失敗或存在衝突"},
        401: {"description": "需要管理員權限"},
        404: {"description": "運費級距不存在"},
        422: {"description": "驗證錯誤"}
    }
)
async def update_shipping_tier(
    tier_id: int,
    tier_data: ShippingTierUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新運費級距
    
    更新指定運費級距的資訊。
    """
    shipping_service = ShippingTierService(db)
    tier = shipping_service.update_shipping_tier(tier_id, tier_data)
    
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="運費級距不存在"
        )
    
    return ShippingTierResponse.model_validate(tier)


@router.delete(
    "/{tier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="🗑️ 刪除運費級距",
    description="""
    ## 🎯 功能描述
    刪除指定的運費級距，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🗑️ 永久刪除級距
    - 📊 清除相關設定
    
    ## ⚠️ 注意事項
    - 刪除操作不可逆
    - 建議先停用級距再刪除
    - 會影響運費計算邏輯
    
    ## 🎯 使用場景
    - 管理後台級距管理
    - 過期政策清理
    - 錯誤設定移除
    """,
    responses={
        204: {"description": "成功刪除運費級距"},
        401: {"description": "需要管理員權限"},
        404: {"description": "運費級距不存在"}
    }
)
async def delete_shipping_tier(
    tier_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    刪除運費級距
    
    永久刪除指定的運費級距。
    """
    shipping_service = ShippingTierService(db)
    success = shipping_service.delete_shipping_tier(tier_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="運費級距不存在"
        )
    
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "運費級距已成功刪除"}
    )


@router.post(
    "/{tier_id}/toggle",
    response_model=ShippingTierResponse,
    summary="🔄 切換運費級距狀態",
    description="""
    ## 🎯 功能描述
    切換運費級距的啟用狀態，需要管理員權限。
    
    ## 📋 功能特點
    - 🔐 需要管理員權限
    - 🔄 一鍵切換啟用/停用
    - 📊 即時生效於運費計算
    
    ## 🎯 使用場景
    - 快速啟用/停用級距
    - 緊急運費政策調整
    - 臨時促銷設定
    """,
    responses={
        200: {"description": "成功切換運費級距狀態"},
        401: {"description": "需要管理員權限"},
        404: {"description": "運費級距不存在"}
    }
)
async def toggle_shipping_tier_status(
    tier_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    切換運費級距狀態
    
    切換指定運費級距的啟用狀態。
    """
    shipping_service = ShippingTierService(db)
    tier = shipping_service.toggle_tier_status(tier_id)
    
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="運費級距不存在"
        )
    
    return ShippingTierResponse.model_validate(tier)


@router.post(
    "/calculate",
    response_model=ShippingCalculationResponse,
    summary="💰 計算運費",
    description="""
    ## 🎯 功能描述
    根據訂單金額計算應付的運費，並提供詳細的運費資訊。
    
    ## 📋 功能特點
    - 💰 自動尋找適用級距
    - 🚚 計算準確運費
    - 📊 提供詳細說明
    - 🔍 處理各種邊界情況
    - 💸 顯示最高運費（原價）
    - 🏷️ 顯示免運費門檻
    - 📈 提示距離免運費還需多少金額
    
    ## 🔍 計算邏輯
    1. 取得所有啟用的運費級距
    2. 按金額範圍尋找適用級距
    3. 如果找不到，使用最高級距
    4. 計算最高運費作為原價
    5. 找出免運費門檻
    6. 計算距離免運費還需多少金額
    7. 返回完整的運費資訊
    
    ## 🎯 使用場景
    - 購物車運費計算
    - 結帳頁面運費顯示
    - 訂單總金額計算
    - 運費政策測試
    """,
    responses={
        200: {
            "description": "成功計算運費",
            "content": {
                "application/json": {
                    "example": {
                        "shipping_fee": "60.00",
                        "free_shipping": False,
                        "applicable_tier": {
                            "id": 1,
                            "name": "基本運費",
                            "min_amount": "0.00",
                            "max_amount": "1000.00",
                            "shipping_fee": "60.00",
                            "free_shipping": False
                        },
                        "message": "適用級距：基本運費，運費 $60.00",
                        "max_shipping_fee": "120.00",
                        "free_shipping_threshold": "1000.00",
                        "amount_needed_for_free_shipping": "500.00",
                        "next_tier": {
                            "id": 2,
                            "name": "免運費級距",
                            "min_amount": "1000.00",
                            "max_amount": None,
                            "shipping_fee": "0.00",
                            "free_shipping": True
                        }
                    }
                }
            }
        },
        400: {"description": "訂單金額參數錯誤"},
        422: {"description": "驗證錯誤"}
    }
)
async def calculate_shipping_fee(
    request: ShippingCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    計算運費
    
    根據訂單金額計算應付的運費和詳細資訊。
    """
    shipping_service = ShippingTierService(db)
    shipping_fee, is_free, applicable_tier, message, max_shipping_fee, free_shipping_threshold, amount_needed_for_free_shipping, next_tier = shipping_service.calculate_detailed_shipping_fee(
        request.order_amount
    )
    
    applicable_tier_response = None
    if applicable_tier:
        applicable_tier_response = ShippingTierResponse.model_validate(applicable_tier)
    
    next_tier_response = None
    if next_tier:
        next_tier_response = ShippingTierResponse.model_validate(next_tier)
    
    return ShippingCalculationResponse(
        shipping_fee=shipping_fee,
        free_shipping=is_free,
        applicable_tier=applicable_tier_response,
        message=message,
        max_shipping_fee=max_shipping_fee,
        free_shipping_threshold=free_shipping_threshold,
        amount_needed_for_free_shipping=amount_needed_for_free_shipping,
        next_tier=next_tier_response
    )


@router.get(
    "/stats/overview",
    response_model=ShippingTierStats,
    summary="📊 取得運費級距統計",
    description="""
    ## 🎯 功能描述
    取得運費級距系統的統計資料，需要管理員權限。
    
    ## 📋 統計內容
    - 📊 總級距數
    - 📈 啟用級距數
    - 📉 停用級距數
    - 🚚 免運費級距數
    - 💰 平均運費金額
    
    ## 🎯 使用場景
    - 管理後台統計面板
    - 運費政策分析
    - 營銷決策支援
    """,
    responses={
        200: {"description": "成功取得運費級距統計"},
        401: {"description": "需要管理員權限"}
    }
)
async def get_shipping_tier_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得運費級距統計
    
    返回運費級距系統的統計資料。
    """
    shipping_service = ShippingTierService(db)
    stats = shipping_service.get_shipping_tier_stats()
    
    return stats 