"""
行銷專案服務層模組

此模組提供行銷專案相關的業務邏輯處理，封裝複雜的資料庫操作和業務規則。

主要功能：
1. 專案管理：創建、更新、刪除、查詢行銷專案
2. 優惠券生成：根據專案設定批次生成唯一優惠券
3. 優惠券分發：將優惠券分發給指定用戶
4. 統計分析：提供詳細的專案和優惠券使用統計
5. 狀態管理：專案狀態轉換和業務邏輯驗證

服務類別：
- CampaignService: 主要服務類，提供所有行銷專案相關的業務方法

業務規則：
1. 優惠碼前綴必須唯一
2. 專案時間範圍驗證
3. 優惠券數量限制控制
4. 狀態轉換邏輯驗證
5. 用戶權限檢查

作者：AI Assistant
創建日期：2024
版本：1.0
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import string
import random

from app.models import (
    MarketingCampaign, CampaignStatus, Coupon, CouponUsage, CouponDistribution,
    User, CouponType, DiscountType
)
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignStats,
    CampaignOverviewStats
)


class CampaignService:
    """行銷專案服務類"""
    
    @staticmethod
    def get_campaigns(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[CampaignStatus] = None,
        active_only: bool = False,
        search: Optional[str] = None
    ) -> List[MarketingCampaign]:
        """獲取行銷專案列表"""
        query = db.query(MarketingCampaign)
        
        if status:
            query = query.filter(MarketingCampaign.status == status)
        
        if active_only:
            query = query.filter(MarketingCampaign.is_active == True)
        
        if search:
            search_filter = or_(
                MarketingCampaign.name.ilike(f"%{search}%"),
                MarketingCampaign.description.ilike(f"%{search}%"),
                MarketingCampaign.coupon_prefix.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.order_by(desc(MarketingCampaign.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_campaigns_count(
        db: Session,
        status: Optional[CampaignStatus] = None,
        active_only: bool = False,
        search: Optional[str] = None
    ) -> int:
        """獲取行銷專案總數量"""
        query = db.query(MarketingCampaign)
        
        if status:
            query = query.filter(MarketingCampaign.status == status)
        
        if active_only:
            query = query.filter(MarketingCampaign.is_active == True)
        
        if search:
            search_filter = or_(
                MarketingCampaign.name.ilike(f"%{search}%"),
                MarketingCampaign.description.ilike(f"%{search}%"),
                MarketingCampaign.coupon_prefix.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.count()
    
    @staticmethod
    def get_campaign(db: Session, campaign_id: int) -> Optional[MarketingCampaign]:
        """獲取單一行銷專案"""
        return db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
    
    @staticmethod
    def create_campaign(db: Session, campaign_data: CampaignCreate) -> MarketingCampaign:
        """創建行銷專案"""
        # 檢查前綴是否已存在
        existing_campaign = db.query(MarketingCampaign).filter(
            MarketingCampaign.coupon_prefix == campaign_data.coupon_prefix
        ).first()
        
        if existing_campaign:
            raise ValueError(f"優惠碼前綴 '{campaign_data.coupon_prefix}' 已存在")
        
        # 建立新專案
        campaign = MarketingCampaign(**campaign_data.model_dump())
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # 如果設定了初始生成數量，則生成優惠券
        if campaign_data.initial_coupons > 0:
            CampaignService.generate_coupons(
                db=db,
                campaign_id=campaign.id,
                count=campaign_data.initial_coupons
            )
        
        return campaign
    
    @staticmethod
    def update_campaign(
        db: Session, 
        campaign_id: int, 
        campaign_data: CampaignUpdate
    ) -> Optional[MarketingCampaign]:
        """更新行銷專案"""
        campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
        if not campaign:
            return None
        
        # 檢查前綴是否已存在（排除當前專案）
        if campaign_data.coupon_prefix:
            existing_campaign = db.query(MarketingCampaign).filter(
                and_(
                    MarketingCampaign.coupon_prefix == campaign_data.coupon_prefix,
                    MarketingCampaign.id != campaign_id
                )
            ).first()
            
            if existing_campaign:
                raise ValueError(f"優惠碼前綴 '{campaign_data.coupon_prefix}' 已存在")
        
        # 更新欄位
        for field, value in campaign_data.model_dump(exclude_unset=True).items():
            setattr(campaign, field, value)
        
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def delete_campaign(db: Session, campaign_id: int) -> bool:
        """刪除行銷專案"""
        campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
        if not campaign:
            return False
        
        # 檢查是否有已使用的優惠券
        used_coupons = db.query(Coupon).filter(
            and_(
                Coupon.campaign_id == campaign_id,
                Coupon.usage_count > 0
            )
        ).count()
        
        if used_coupons > 0:
            raise ValueError("無法刪除已有優惠券被使用的專案")
        
        db.delete(campaign)
        db.commit()
        
        return True
    
    @staticmethod
    def generate_coupons(
        db: Session,
        campaign_id: int,
        count: int,
        auto_distribute: bool = False,
        target_users: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """為行銷專案生成優惠券"""
        campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
        if not campaign:
            raise ValueError("行銷專案不存在")
        
        # 檢查是否還可以生成更多優惠券
        remaining = campaign.total_coupons - campaign.generated_count
        if count > remaining:
            raise ValueError(f"超過可生成數量限制，剩餘可生成：{remaining}")
        
        generated_coupons = []
        generated_count = 0
        
        for _ in range(count):
            try:
                # 生成唯一的優惠碼
                coupon_code = CampaignService._generate_coupon_code(db, campaign.coupon_prefix)
                
                # 建立優惠券
                coupon = Coupon(
                    code=coupon_code,
                    name=f"{campaign.name} - {coupon_code}",
                    description=campaign.description,
                    coupon_type=CouponType(campaign.coupon_type),
                    discount_type=DiscountType(campaign.discount_type),
                    discount_value=campaign.discount_value,
                    minimum_amount=campaign.minimum_amount,
                    maximum_discount=campaign.maximum_discount,
                    product_id=campaign.product_id,
                    campaign_id=campaign_id,
                    valid_from=campaign.coupon_valid_from,
                    valid_to=campaign.coupon_valid_to,
                    is_active=True
                )
                
                db.add(coupon)
                generated_coupons.append(coupon)
                generated_count += 1
                
            except Exception as e:
                print(f"生成優惠券時發生錯誤: {e}")
                continue
        
        # 更新專案統計
        campaign.generated_count += generated_count
        
        db.commit()
        
        # 如果需要自動分發
        if auto_distribute and target_users:
            CampaignService.distribute_coupons(
                db=db,
                campaign_id=campaign_id,
                user_ids=target_users,
                coupon_count=1,
                notes="自動分發"
            )
        
        return {
            "message": f"成功生成 {generated_count} 張優惠券",
            "generated_count": generated_count,
            "total_generated": campaign.generated_count,
            "remaining": campaign.total_coupons - campaign.generated_count
        }
    
    @staticmethod
    def distribute_coupons(
        db: Session,
        campaign_id: int,
        user_ids: List[int],
        coupon_count: int = 1,
        notes: Optional[str] = None,
        distributed_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """分發行銷專案優惠券"""
        campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
        if not campaign:
            raise ValueError("行銷專案不存在")
        
        # 獲取可用的優惠券
        available_coupons = db.query(Coupon).filter(
            and_(
                Coupon.campaign_id == campaign_id,
                Coupon.is_active == True
            )
        ).limit(len(user_ids) * coupon_count).all()
        
        if len(available_coupons) < len(user_ids) * coupon_count:
            raise ValueError("可用優惠券不足，請先生成更多優惠券")
        
        distributions = []
        distributed_count = 0
        coupon_index = 0
        
        for user_id in user_ids:
            # 檢查用戶是否存在
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                continue
            
            # 為該用戶分發指定數量的優惠券
            for _ in range(coupon_count):
                if coupon_index >= len(available_coupons):
                    break
                
                coupon = available_coupons[coupon_index]
                
                # 建立分發記錄
                distribution = CouponDistribution(
                    coupon_id=coupon.id,
                    user_id=user_id,
                    distributed_by=distributed_by,
                    notes=notes
                )
                
                db.add(distribution)
                distributions.append(distribution)
                distributed_count += 1
                coupon_index += 1
        
        # 更新專案統計
        campaign.distributed_count += distributed_count
        
        db.commit()
        
        return {
            "message": f"成功分發 {distributed_count} 張優惠券給 {len(user_ids)} 位用戶",
            "distributed_count": distributed_count,
            "total_distributed": campaign.distributed_count
        }
    
    @staticmethod
    def get_campaign_stats(db: Session, campaign_id: int) -> Optional[CampaignStats]:
        """獲取行銷專案統計資料"""
        campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
        if not campaign:
            return None
        
        # 計算使用率和分發率
        usage_rate = 0.0
        distribution_rate = 0.0
        conversion_rate = 0.0
        
        if campaign.generated_count > 0:
            usage_rate = (campaign.used_count / campaign.generated_count) * 100
            distribution_rate = (campaign.distributed_count / campaign.generated_count) * 100
            
            if campaign.distributed_count > 0:
                conversion_rate = (campaign.used_count / campaign.distributed_count) * 100
        
        return CampaignStats(
            campaign_id=campaign.id,
            campaign_name=campaign.name,
            total_coupons=campaign.total_coupons,
            generated_count=campaign.generated_count,
            distributed_count=campaign.distributed_count,
            used_count=campaign.used_count,
            total_discount_amount=campaign.total_discount_amount,
            usage_rate=usage_rate,
            distribution_rate=distribution_rate,
            conversion_rate=conversion_rate,
            remaining_coupons=campaign.total_coupons - campaign.generated_count
        )
    
    @staticmethod
    def get_campaign_coupons(
        db: Session,
        campaign_id: int,
        skip: int = 0,
        limit: int = 20,
        used_only: bool = False,
        available_only: bool = False
    ) -> List[Coupon]:
        """獲取行銷專案的優惠券列表"""
        query = db.query(Coupon).filter(Coupon.campaign_id == campaign_id)
        
        if used_only:
            query = query.filter(Coupon.usage_count > 0)
        
        if available_only:
            query = query.filter(
                and_(
                    Coupon.is_active == True,
                    Coupon.usage_count == 0
                )
            )
        
        return query.order_by(desc(Coupon.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_campaign_status(
        db: Session, 
        campaign_id: int, 
        status: CampaignStatus
    ) -> Optional[MarketingCampaign]:
        """更新行銷專案狀態"""
        campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
        if not campaign:
            return None
        
        # 業務邏輯驗證
        if status == CampaignStatus.ACTIVE:
            now = datetime.now(timezone.utc)
            if campaign.campaign_start > now:
                raise ValueError("專案開始時間尚未到達，無法啟動")
            if campaign.campaign_end < now:
                raise ValueError("專案已過期，無法啟動")
        
        campaign.status = status
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def get_overview_stats(db: Session) -> CampaignOverviewStats:
        """獲取行銷專案總覽統計"""
        # 統計各狀態的專案數量
        stats_query = db.query(
            MarketingCampaign.status,
            func.count(MarketingCampaign.id).label('count')
        ).group_by(MarketingCampaign.status).all()
        
        status_counts = {status.value: 0 for status in CampaignStatus}
        for status, count in stats_query:
            status_counts[status.value] = count
        
        # 統計總數
        total_campaigns = sum(status_counts.values())
        
        # 統計優惠券數據
        coupon_stats = db.query(
            func.sum(MarketingCampaign.generated_count).label('total_generated'),
            func.sum(MarketingCampaign.used_count).label('total_used'),
            func.sum(MarketingCampaign.total_discount_amount).label('total_discount')
        ).first()
        
        # 計算平均使用率
        campaigns_with_coupons = db.query(MarketingCampaign).filter(
            MarketingCampaign.generated_count > 0
        ).all()
        
        average_usage_rate = 0.0
        if campaigns_with_coupons:
            total_rate = sum(
                (campaign.used_count / campaign.generated_count) * 100
                for campaign in campaigns_with_coupons
            )
            average_usage_rate = total_rate / len(campaigns_with_coupons)
        
        return CampaignOverviewStats(
            total_campaigns=total_campaigns,
            active_campaigns=status_counts[CampaignStatus.ACTIVE.value],
            draft_campaigns=status_counts[CampaignStatus.DRAFT.value],
            completed_campaigns=status_counts[CampaignStatus.COMPLETED.value],
            total_coupons_generated=coupon_stats.total_generated or 0,
            total_coupons_used=coupon_stats.total_used or 0,
            total_discount_amount=coupon_stats.total_discount or 0,
            average_usage_rate=average_usage_rate
        )
    
    @staticmethod
    def _generate_coupon_code(db: Session, prefix: str) -> str:
        """生成唯一的優惠碼"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            # 生成隨機後綴
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            code = f"{prefix}-{suffix}"
            
            # 檢查是否已存在
            existing = db.query(Coupon).filter(Coupon.code == code).first()
            if not existing:
                return code
        
        raise ValueError("無法生成唯一的優惠碼") 