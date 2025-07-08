"""
行銷專案 API 路由模組

此模組定義了行銷專案管理相關的 REST API 端點，提供完整的 CRUD 操作和業務功能。

主要 API 端點：
- GET /campaigns: 獲取行銷專案列表（支援分頁、篩選、搜尋）
- POST /campaigns: 創建新的行銷專案
- GET /campaigns/stats/overview: 獲取專案總覽統計
- GET /campaigns/{id}: 獲取單一行銷專案詳情
- PUT /campaigns/{id}: 更新行銷專案
- DELETE /campaigns/{id}: 刪除行銷專案
- POST /campaigns/{id}/generate-coupons: 為專案生成優惠券
- POST /campaigns/{id}/distribute-coupons: 分發專案優惠券
- GET /campaigns/{id}/stats: 獲取專案統計資料
- GET /campaigns/{id}/coupons: 獲取專案優惠券列表
- PATCH /campaigns/{id}/status: 更新專案狀態

權限控制：
- 所有端點都需要管理員權限
- 使用 JWT token 進行身份驗證

作者：AI Assistant
創建日期：2024
版本：1.0
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models import User, MarketingCampaign, CampaignStatus, Coupon
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse,
    CampaignStats, CampaignCouponGenerate, CampaignCouponDistribute, CampaignOverviewStats
)
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("/stats/overview", response_model=CampaignOverviewStats)
async def get_campaigns_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取行銷專案總覽統計"""
    print(f"DEBUG: 進入get_campaigns_overview，用戶: {current_user.username if current_user else 'None'}")
    
    if not current_user.is_admin:
        print(f"DEBUG: 用戶 {current_user.username} 不是管理員")
        raise HTTPException(status_code=403, detail="只有管理員可以查看統計資料")
    
    print("DEBUG: 開始調用CampaignService.get_overview_stats")
    try:
        stats = CampaignService.get_overview_stats(db=db)
        print(f"DEBUG: 服務返回統計: {stats}")
        print(f"DEBUG: 統計類型: {type(stats)}")
        return stats
    except Exception as e:
        print(f"DEBUG: get_overview_stats異常: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/", response_model=CampaignListResponse)
async def get_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[CampaignStatus] = Query(None),
    active_only: bool = Query(False),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取行銷專案列表"""
    print(f"DEBUG: 進入get_campaigns，用戶: {current_user.username if current_user else 'None'}")
    
    if not current_user.is_admin:
        print(f"DEBUG: 用戶 {current_user.username} 不是管理員")
        raise HTTPException(status_code=403, detail="只有管理員可以查看行銷專案")
    
    print(f"DEBUG: 參數 - skip: {skip}, limit: {limit}, status: {status}")
    
    try:
        campaigns = CampaignService.get_campaigns(
            db=db,
            skip=skip,
            limit=limit,
            status=status,
            active_only=active_only,
            search=search
        )
        print(f"DEBUG: 獲取到 {len(campaigns)} 個專案")
        
        # 明確轉換為CampaignResponse
        campaign_responses = [CampaignResponse.model_validate(campaign) for campaign in campaigns]
        print(f"DEBUG: 轉換了 {len(campaign_responses)} 個響應對象")
        
        total = CampaignService.get_campaigns_count(
            db=db,
            status=status,
            active_only=active_only,
            search=search
        )
        print(f"DEBUG: 總數: {total}")
        
        result = CampaignListResponse(
            items=campaign_responses,
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit
        )
        print(f"DEBUG: 返回結果類型: {type(result)}")
        return result
    except Exception as e:
        print(f"DEBUG: get_campaigns異常: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """創建行銷專案"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以創建行銷專案")
    
    try:
        campaign = CampaignService.create_campaign(db=db, campaign_data=campaign_data)
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{campaign_id}/stats", response_model=CampaignStats)
async def get_campaign_stats(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取行銷專案統計資料"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以查看統計資料")
    
    stats = CampaignService.get_campaign_stats(db=db, campaign_id=campaign_id)
    if not stats:
        raise HTTPException(status_code=404, detail="行銷專案不存在")
    
    return stats


@router.get("/{campaign_id}/coupons")
async def get_campaign_coupons(
    campaign_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    used_only: bool = Query(False),
    available_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取行銷專案的優惠券列表"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以查看優惠券列表")
    
    coupons = CampaignService.get_campaign_coupons(
        db=db,
        campaign_id=campaign_id,
        skip=skip,
        limit=limit,
        used_only=used_only,
        available_only=available_only
    )
    
    return coupons


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取單一行銷專案"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以查看行銷專案")
    
    campaign = CampaignService.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="行銷專案不存在")
    
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新行銷專案"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以更新行銷專案")
    
    try:
        campaign = CampaignService.update_campaign(db=db, campaign_id=campaign_id, campaign_data=campaign_data)
        if not campaign:
            raise HTTPException(status_code=404, detail="行銷專案不存在")
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """刪除行銷專案"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以刪除行銷專案")
    
    success = CampaignService.delete_campaign(db=db, campaign_id=campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="行銷專案不存在")
    
    return {"message": "行銷專案已刪除"}


@router.post("/{campaign_id}/generate-coupons")
async def generate_campaign_coupons(
    campaign_id: int,
    generate_data: CampaignCouponGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """為行銷專案生成優惠券"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以生成優惠券")
    
    try:
        result = CampaignService.generate_coupons(
            db=db,
            campaign_id=campaign_id,
            count=generate_data.count,
            auto_distribute=generate_data.auto_distribute,
            target_users=generate_data.target_users
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/distribute-coupons")
async def distribute_campaign_coupons(
    campaign_id: int,
    distribute_data: CampaignCouponDistribute,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """分發行銷專案優惠券"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以分發優惠券")
    
    try:
        result = CampaignService.distribute_coupons(
            db=db,
            campaign_id=campaign_id,
            user_ids=distribute_data.user_ids,
            coupon_count=distribute_data.coupon_count,
            notes=distribute_data.notes,
            distributed_by=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: int,
    status: CampaignStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新行銷專案狀態"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理員可以更新專案狀態")
    
    try:
        campaign = CampaignService.update_campaign_status(db=db, campaign_id=campaign_id, status=status)
        if not campaign:
            raise HTTPException(status_code=404, detail="行銷專案不存在")
        return {"message": f"專案狀態已更新為 {status.value}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 