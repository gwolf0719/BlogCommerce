"""
優惠券 API 路由模組

此模組定義了優惠券管理和使用相關的 REST API 端點，提供完整的優惠券生命週期管理功能。

主要功能分類：

1. **管理員優惠券管理**：
   - POST /coupons: 創建單一優惠券
   - POST /coupons/batch: 批次創建優惠券
   - GET /coupons: 獲取優惠券列表（支援篩選）
   - GET /coupons/{id}: 獲取單一優惠券詳情
   - PUT /coupons/{id}: 更新優惠券
   - DELETE /coupons/{id}: 刪除優惠券

2. **優惠券分發管理**：
   - POST /coupons/{id}/distribute: 分發優惠券給特定用戶
   - POST /coupons/{id}/distribute/batch: 批次分發優惠券
   - GET /coupons/{id}/distributions: 查看分發記錄

3. **使用記錄管理**：
   - GET /coupons/{id}/usage: 查看特定優惠券使用記錄
   - GET /coupons/usage/all: 查看所有使用記錄
   - GET /coupons/stats/overview: 獲取優惠券統計資料

4. **用戶優惠券功能**：
   - POST /coupons/validate: 驗證優惠券有效性
   - GET /coupons/my-coupons: 獲取用戶可用優惠券
   - GET /coupons/code/{code}: 通過代碼查詢優惠券

5. **內部系統接口**：
   - POST /coupons/internal/apply: 內部訂單優惠券應用

權限控制：
- 管理功能需要管理員權限
- 用戶功能需要用戶登入
- 部分查詢功能支援訪客使用

作者：AI Assistant
創建日期：2024
版本：1.0
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.auth import get_current_user, get_current_admin_user, get_current_user_optional
from app.models.user import User
from app.models.coupon import CouponType, DiscountType
from app.services.coupon_service import CouponService
from app.schemas.coupon import (
    CouponCreate, CouponUpdate, CouponResponse, CouponListResponse,
    CouponBatchCreate, CouponBatchCreateResponse, CouponUsageResponse,
    CouponDistributionCreate, CouponDistributionBatch, CouponDistributionResponse,
    CouponValidationRequest, CouponValidationResponse, CouponStats, UserCouponResponse
)

router = APIRouter(prefix="/api/coupons", tags=["優惠券"])


def get_coupon_service(db: Session = Depends(get_db)) -> CouponService:
    return CouponService(db)


# ==============================================
# 管理員優惠券管理
# ==============================================

@router.post("/", response_model=CouponResponse)
async def create_coupon(
    coupon_data: CouponCreate,
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """建立優惠券（管理員）"""
    try:
        coupon = coupon_service.create_coupon(coupon_data)
        return coupon
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch", response_model=CouponBatchCreateResponse)
async def batch_create_coupons(
    batch_data: CouponBatchCreate,
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """批次建立優惠券（管理員）"""
    try:
        created_coupons, errors = coupon_service.batch_create_coupons(batch_data, current_admin.id)  # type: ignore
        
        return CouponBatchCreateResponse(
            success_count=len(created_coupons),
            failed_count=len(errors),
            total_count=batch_data.count,
            created_codes=[coupon.code for coupon in created_coupons],  # type: ignore
            errors=errors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CouponListResponse])
async def get_coupons(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active_only: Optional[bool] = Query(None, description="只顯示啟用的優惠券"),
    coupon_type: Optional[CouponType] = Query(None, description="按類型過濾"),
    expired_only: Optional[bool] = Query(None, description="只顯示已過期的優惠券"),
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """取得優惠券列表（管理員）"""
    coupons = coupon_service.get_coupons(
        skip=skip,
        limit=limit,
        active_only=active_only,
        coupon_type=coupon_type,
        expired_only=expired_only
    )
    return coupons


@router.get("/{coupon_id}", response_model=CouponResponse)
async def get_coupon(
    coupon_id: int,
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """取得單一優惠券（管理員）"""
    coupon = coupon_service.get_coupon_by_id(coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="優惠券不存在")
    return coupon


@router.put("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: int,
    update_data: CouponUpdate,
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """更新優惠券（管理員）"""
    coupon = coupon_service.update_coupon(coupon_id, update_data)
    if not coupon:
        raise HTTPException(status_code=404, detail="優惠券不存在")
    return coupon


@router.delete("/{coupon_id}")
async def delete_coupon(
    coupon_id: int,
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """刪除優惠券（管理員）"""
    try:
        success = coupon_service.delete_coupon(coupon_id)
        if not success:
            raise HTTPException(status_code=404, detail="優惠券不存在")
        return {"message": "優惠券已刪除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==============================================
# 優惠券分發管理
# ==============================================

@router.post("/{coupon_id}/distribute", response_model=CouponDistributionResponse)
async def distribute_coupon(
    coupon_id: int,
    distribution_data: CouponDistributionCreate,
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """分發優惠券給用戶（管理員）"""
    try:
        distribution = coupon_service.distribute_coupon(
            coupon_id=distribution_data.coupon_id,
            user_id=distribution_data.user_id,
            distributed_by=current_admin.id,
            notes=distribution_data.notes
        )
        return distribution
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{coupon_id}/distribute/batch", response_model=dict)
async def batch_distribute_coupons(
    coupon_id: int,
    batch_data: CouponDistributionBatch,
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """批次分發優惠券（管理員）"""
    try:
        distributions, errors = coupon_service.batch_distribute_coupons(
            coupon_id=batch_data.coupon_id,
            user_ids=batch_data.user_ids,
            distributed_by=current_admin.id,
            notes=batch_data.notes
        )
        
        return {
            "success_count": len(distributions),
            "failed_count": len(errors),
            "total_count": len(batch_data.user_ids),
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{coupon_id}/distributions", response_model=List[CouponDistributionResponse])
async def get_coupon_distributions(
    coupon_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """取得優惠券分發記錄（管理員）"""
    distributions = coupon_service.get_coupon_distribution_records(
        coupon_id=coupon_id,
        skip=skip,
        limit=limit
    )
    return distributions


# ==============================================
# 使用記錄管理
# ==============================================

@router.get("/{coupon_id}/usage", response_model=List[CouponUsageResponse])
async def get_coupon_usage(
    coupon_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """取得優惠券使用記錄（管理員）"""
    usage_records = coupon_service.get_coupon_usage_records(
        coupon_id=coupon_id,
        skip=skip,
        limit=limit
    )
    return usage_records


@router.get("/usage/all", response_model=List[CouponUsageResponse])
async def get_all_usage_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = Query(None, description="按用戶過濾"),
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """取得所有使用記錄（管理員）"""
    usage_records = coupon_service.get_coupon_usage_records(
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    return usage_records


# ==============================================
# 統計資料
# ==============================================

@router.get("/stats/overview", response_model=CouponStats)
async def get_coupon_stats(
    current_admin: User = Depends(get_current_admin_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """取得優惠券統計資料（管理員）"""
    stats = coupon_service.get_coupon_stats()
    return stats


# ==============================================
# 用戶端優惠券功能
# ==============================================

@router.post("/validate", response_model=CouponValidationResponse)
async def validate_coupon(
    validation_request: CouponValidationRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """驗證優惠券"""
    # 如果有登入用戶，使用用戶ID
    if current_user:
        validation_request.user_id = current_user.id
    
    validation_result = coupon_service.validate_coupon(validation_request)
    return validation_result


@router.get("/my-coupons", response_model=List[UserCouponResponse])
async def get_my_coupons(
    available_only: bool = Query(True, description="只顯示可用的優惠券"),
    current_user: User = Depends(get_current_user),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """取得我的優惠券"""
    coupons = coupon_service.get_user_coupons(
        user_id=current_user.id,
        available_only=available_only
    )
    return coupons


@router.get("/code/{code}", response_model=CouponResponse)
async def get_coupon_by_code(
    code: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """根據代碼取得優惠券資訊"""
    coupon = coupon_service.get_coupon_by_code(code)
    if not coupon:
        raise HTTPException(status_code=404, detail="優惠券不存在")
    
    # 檢查用戶是否有權限查看此優惠券
    if current_user:
        # 檢查是否已分發給用戶
        distributions = coupon_service.get_coupon_distribution_records(
            coupon_id=coupon.id,
            user_id=current_user.id,
            limit=1
        )
        if not distributions and not coupon.is_valid():
            raise HTTPException(status_code=403, detail="無權限查看此優惠券")
    
    return coupon


# ==============================================
# 內部 API（給訂單系統使用）
# ==============================================

@router.post("/internal/apply")
async def apply_coupon_to_order(
    data: dict,
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """將優惠券套用到訂單（內部 API）"""
    try:
        coupon_code = data.get("coupon_code")
        user_id = data.get("user_id")
        order_id = data.get("order_id")
        # 支援 amount 和 total_amount 兩種參數名
        amount = data.get("amount") or data.get("total_amount", 0)
        total_amount = Decimal(str(amount))
        product_id = data.get("product_id")
        
        # 驗證輸入數據
        if not coupon_code:
            return {
                "success": False,
                "message": "優惠券代碼不能為空"
            }
        
        if total_amount <= 0:
            return {
                "success": False,
                "message": "訂單金額必須大於0"
            }
        
        # 驗證優惠券
        validation_request = CouponValidationRequest(
            code=coupon_code,
            user_id=user_id,
            product_id=product_id,
            amount=total_amount
        )
        
        validation_result = coupon_service.validate_coupon(validation_request)
        
        if not validation_result.is_valid:
            return {
                "success": False,
                "message": validation_result.message
            }
        
        # 使用優惠券
        coupon = coupon_service.get_coupon_by_code(coupon_code)
        if not coupon:
            return {
                "success": False,
                "message": "優惠券不存在"
            }
        
        usage = coupon_service.use_coupon(
            coupon_id=coupon.id,
            user_id=user_id,
            order_id=order_id,
            discount_amount=validation_result.discount_amount
        )
        
        return {
            "success": True,
            "message": "優惠券套用成功",
            "discount_amount": float(validation_result.discount_amount),
            "free_shipping": validation_result.free_shipping,
            "usage_id": usage.id
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        } 