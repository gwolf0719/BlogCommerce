"""
優惠券服務層模組

此模組提供優惠券系統的核心業務邏輯處理，封裝複雜的優惠券管理和使用流程。

主要功能分類：

1. **優惠券生命週期管理**：
   - 優惠券創建（單一/批次）
   - 優惠券代碼生成（確保唯一性）
   - 優惠券更新和刪除
   - 優惠券查詢和列表

2. **優惠券驗證和使用**：
   - 優惠券有效性驗證
   - 折扣金額計算
   - 使用條件檢查（最低消費、商品限制等）
   - 使用記錄建立和追蹤

3. **優惠券分發管理**：
   - 手動分發優惠券給特定用戶
   - 批次分發優惠券
   - 分發記錄追蹤
   - 自動分發機制

4. **統計和報表**：
   - 優惠券使用統計
   - 分發統計
   - 總覽數據
   - 用戶優惠券查詢

服務類別：
- CouponService: 主要服務類，提供所有優惠券相關業務方法

業務規則：
1. 優惠券代碼必須唯一
2. 支援多種優惠類型（商品折扣/整筆折扣/免運費）
3. 時間有效期驗證
4. 使用條件限制（最低消費、商品限制）
5. 防止重複使用
6. 分發記錄追蹤

作者：AI Assistant
創建日期：2024
版本：1.0
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import string
import random

from app.models.coupon import Coupon, CouponUsage, CouponDistribution, CouponType, DiscountType
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.schemas.coupon import (
    CouponCreate, CouponUpdate, CouponBatchCreate, CouponDistributionCreate,
    CouponValidationRequest, CouponValidationResponse, CouponStats
)


class CouponService:
    """優惠券服務類"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_coupon_code(self, prefix: str = "", length: int = 8) -> str:
        """生成優惠券代碼"""
        chars = string.ascii_uppercase + string.digits
        if prefix:
            code = prefix + "-" + ''.join(random.choices(chars, k=length))
        else:
            code = ''.join(random.choices(chars, k=length))
        
        # 確保代碼唯一
        while self.db.query(Coupon).filter(Coupon.code == code).first():
            if prefix:
                code = prefix + "-" + ''.join(random.choices(chars, k=length))
            else:
                code = ''.join(random.choices(chars, k=length))
        
        return code
    
    def create_coupon(self, coupon_data: CouponCreate, code: str = None) -> Coupon:
        """建立單一優惠券"""
        if not code:
            code = self.generate_coupon_code()
        
        # 驗證商品是否存在（如果是商品折扣）
        if coupon_data.coupon_type == CouponType.PRODUCT_DISCOUNT:
            if not coupon_data.product_id:
                raise ValueError("商品折扣券必須指定商品")
            
            product = self.db.query(Product).filter(Product.id == coupon_data.product_id).first()
            if not product:
                raise ValueError("指定的商品不存在")
        
        # 建立優惠券
        coupon = Coupon(
            code=code,
            name=coupon_data.name,
            description=coupon_data.description,
            coupon_type=coupon_data.coupon_type,
            discount_type=coupon_data.discount_type,
            discount_value=coupon_data.discount_value,
            minimum_amount=coupon_data.minimum_amount,
            maximum_discount=coupon_data.maximum_discount,
            product_id=coupon_data.product_id,
            valid_from=coupon_data.valid_from,
            valid_to=coupon_data.valid_to,
            is_active=coupon_data.is_active
        )
        
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        
        return coupon
    
    def batch_create_coupons(self, batch_data: CouponBatchCreate, created_by: int) -> Tuple[List[Coupon], List[str]]:
        """批次建立優惠券"""
        created_coupons = []
        errors = []
        
        for i in range(batch_data.count):
            try:
                code = self.generate_coupon_code(batch_data.code_prefix)
                coupon = self.create_coupon(batch_data.base_coupon, code)
                created_coupons.append(coupon)
                
                # 如果需要自動分發
                if batch_data.auto_distribute and batch_data.target_users:
                    for user_id in batch_data.target_users:
                        self.distribute_coupon(coupon.id, user_id, created_by)
                
            except Exception as e:
                errors.append(f"建立第 {i+1} 個優惠券時發生錯誤：{str(e)}")
        
        return created_coupons, errors
    
    def update_coupon(self, coupon_id: int, update_data: CouponUpdate) -> Optional[Coupon]:
        """更新優惠券"""
        coupon = self.db.query(Coupon).filter(Coupon.id == coupon_id).first()
        if not coupon:
            return None
        
        # 更新欄位
        for field, value in update_data.dict(exclude_unset=True).items():
            if hasattr(coupon, field):
                setattr(coupon, field, value)
        
        self.db.commit()
        self.db.refresh(coupon)
        
        return coupon
    
    def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        """根據代碼取得優惠券"""
        return self.db.query(Coupon).filter(Coupon.code == code).first()
    
    def get_coupon_by_id(self, coupon_id: int) -> Optional[Coupon]:
        """根據ID取得優惠券"""
        return self.db.query(Coupon).filter(Coupon.id == coupon_id).first()
    
    def get_coupons(self, 
                   skip: int = 0, 
                   limit: int = 50,
                   active_only: bool = None,
                   coupon_type: CouponType = None,
                   expired_only: bool = None,
                   campaign_id: Optional[int] = None) -> List[Coupon]:
        """取得優惠券列表（只返回有關聯行銷專案的優惠券）"""
        query = self.db.query(Coupon)
        
        # 強制要求優惠券必須關聯行銷專案（符合業務邏輯）
        query = query.filter(Coupon.campaign_id.isnot(None))
        
        if active_only is not None:
            query = query.filter(Coupon.is_active == active_only)
        
        if coupon_type:
            query = query.filter(Coupon.coupon_type == coupon_type)
        
        if expired_only is not None:
            now = datetime.now(timezone.utc)
            if expired_only:
                query = query.filter(Coupon.valid_to < now)
            else:
                query = query.filter(Coupon.valid_to >= now)
        
        if campaign_id is not None:
            query = query.filter(Coupon.campaign_id == campaign_id)
        
        return query.order_by(Coupon.created_at.desc()).offset(skip).limit(limit).all()
    
    def validate_coupon(self, validation_request: CouponValidationRequest) -> CouponValidationResponse:
        """驗證優惠券"""
        coupon = self.get_coupon_by_code(validation_request.code)
        
        if not coupon:
            return CouponValidationResponse(
                is_valid=False,
                message="優惠券不存在"
            )
        
        # 檢查優惠券狀態
        if not coupon.is_active:
            return CouponValidationResponse(
                is_valid=False,
                message="優惠券已停用"
            )
        
        # 檢查有效期
        if not coupon.is_valid():
            return CouponValidationResponse(
                is_valid=False,
                message="優惠券已過期"
            )
        
        # 檢查是否已使用過（一個代碼只能使用一次）
        if validation_request.user_id:
            usage = self.db.query(CouponUsage).filter(
                and_(
                    CouponUsage.coupon_id == coupon.id,
                    CouponUsage.user_id == validation_request.user_id
                )
            ).first()
            if usage:
                return CouponValidationResponse(
                    is_valid=False,
                    message="此優惠券已使用過"
                )
        
        # 檢查最低消費金額
        if coupon.minimum_amount and validation_request.amount < coupon.minimum_amount:
            return CouponValidationResponse(
                is_valid=False,
                message=f"最低消費金額為 ${coupon.minimum_amount}"
            )
        
        # 檢查商品限制
        if coupon.coupon_type == CouponType.PRODUCT_DISCOUNT:
            if not validation_request.product_id or validation_request.product_id != coupon.product_id:
                return CouponValidationResponse(
                    is_valid=False,
                    message="此優惠券只適用於特定商品"
                )
        
        # 計算折扣
        discount_amount = coupon.calculate_discount(validation_request.amount, validation_request.product_id)
        free_shipping = coupon.coupon_type == CouponType.FREE_SHIPPING
        
        # 轉換為 CouponResponse 類型
        from app.schemas.coupon import CouponResponse
        coupon_response = CouponResponse.model_validate(coupon)
        
        return CouponValidationResponse(
            is_valid=True,
            message="優惠券有效",
            discount_amount=discount_amount,
            free_shipping=free_shipping,
            coupon=coupon_response
        )
    
    def use_coupon(self, coupon_id: int, user_id: Optional[int], order_id: int, discount_amount: Decimal) -> CouponUsage:
        """使用優惠券"""
        coupon = self.get_coupon_by_id(coupon_id)
        if not coupon:
            raise ValueError("優惠券不存在")
        
        # 建立使用記錄
        usage = CouponUsage(
            coupon_id=coupon_id,
            user_id=user_id,
            order_id=order_id,
            discount_amount=discount_amount
        )
        
        # 更新使用次數
        coupon.usage_count += 1
        
        self.db.add(usage)
        self.db.commit()
        self.db.refresh(usage)
        
        return usage
    
    def distribute_coupon(self, coupon_id: int, user_id: int, distributed_by: int, notes: str = None) -> CouponDistribution:
        """分發優惠券給用戶"""
        from app.models.user import User
        
        # 檢查優惠券是否存在
        coupon = self.get_coupon_by_id(coupon_id)
        if not coupon:
            raise ValueError("優惠券不存在")
        
        # 檢查用戶是否存在
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用戶不存在")
        
        # 檢查是否已分發過
        existing = self.db.query(CouponDistribution).filter(
            and_(
                CouponDistribution.coupon_id == coupon_id,
                CouponDistribution.user_id == user_id
            )
        ).first()
        
        if existing:
            raise ValueError("此優惠券已分發給該用戶")
        
        # 建立分發記錄
        distribution = CouponDistribution(
            coupon_id=coupon_id,
            user_id=user_id,
            distributed_by=distributed_by,
            notes=notes
        )
        
        self.db.add(distribution)
        self.db.commit()
        self.db.refresh(distribution)
        
        return distribution
    
    def batch_distribute_coupons(self, coupon_id: int, user_ids: List[int], distributed_by: int, notes: str = None) -> Tuple[List[CouponDistribution], List[str]]:
        """批次分發優惠券"""
        distributions = []
        errors = []
        
        for user_id in user_ids:
            try:
                distribution = self.distribute_coupon(coupon_id, user_id, distributed_by, notes)
                distributions.append(distribution)
            except Exception as e:
                errors.append(f"分發給用戶 {user_id} 時發生錯誤：{str(e)}")
        
        return distributions, errors
    
    def get_user_coupons(self, user_id: int, available_only: bool = True) -> List[Coupon]:
        """取得用戶的優惠券"""
        query = self.db.query(Coupon).join(CouponDistribution).filter(
            CouponDistribution.user_id == user_id
        )
        
        if available_only:
            # 只顯示可用的（未使用且未過期）
            now = datetime.now(timezone.utc)
            query = query.filter(
                and_(
                    Coupon.is_active == True,
                    Coupon.valid_to >= now,
                    ~Coupon.id.in_(
                        self.db.query(CouponUsage.coupon_id).filter(
                            CouponUsage.user_id == user_id
                        )
                    )
                )
            )
        
        return query.order_by(Coupon.valid_to.asc()).all()
    
    def get_coupon_usage_records(self, coupon_id: int = None, user_id: int = None, skip: int = 0, limit: int = 50) -> List[CouponUsage]:
        """取得使用記錄"""
        query = self.db.query(CouponUsage)
        
        if coupon_id:
            query = query.filter(CouponUsage.coupon_id == coupon_id)
        
        if user_id:
            query = query.filter(CouponUsage.user_id == user_id)
        
        return query.order_by(CouponUsage.used_at.desc()).offset(skip).limit(limit).all()
    
    def get_coupon_distribution_records(self, coupon_id: int = None, user_id: int = None, skip: int = 0, limit: int = 50) -> List[CouponDistribution]:
        """取得分發記錄"""
        query = self.db.query(CouponDistribution)
        
        if coupon_id:
            query = query.filter(CouponDistribution.coupon_id == coupon_id)
        
        if user_id:
            query = query.filter(CouponDistribution.user_id == user_id)
        
        return query.order_by(CouponDistribution.distributed_at.desc()).offset(skip).limit(limit).all()
    
    def get_coupon_stats(self) -> CouponStats:
        """取得優惠券統計（只統計有關聯行銷專案的優惠券）"""
        now = datetime.now(timezone.utc)
        
        # 基本統計（只統計有行銷專案的優惠券）
        total_coupons = self.db.query(Coupon).filter(Coupon.campaign_id.isnot(None)).count()
        active_coupons = self.db.query(Coupon).filter(
            and_(
                Coupon.campaign_id.isnot(None),
                Coupon.is_active == True, 
                Coupon.valid_to >= now
            )
        ).count()
        expired_coupons = self.db.query(Coupon).filter(
            and_(
                Coupon.campaign_id.isnot(None),
                Coupon.valid_to < now
            )
        ).count()
        
        used_coupons = self.db.query(CouponUsage).join(Coupon).filter(
            Coupon.campaign_id.isnot(None)
        ).count()
        unused_coupons = total_coupons - used_coupons
        
        # 總折扣金額（只計算有行銷專案的優惠券）
        total_discount = self.db.query(func.sum(CouponUsage.discount_amount)).join(Coupon).filter(
            Coupon.campaign_id.isnot(None)
        ).scalar() or Decimal('0')
        
        # 按類型統計（只統計有行銷專案的優惠券）
        by_type = {}
        for coupon_type in CouponType:
            count = self.db.query(Coupon).filter(
                and_(
                    Coupon.campaign_id.isnot(None),
                    Coupon.coupon_type == coupon_type
                )
            ).count()
            by_type[coupon_type.value] = count
        
        # 按月份統計（最近12個月，只統計有行銷專案的優惠券）
        by_month = {}
        from dateutil.relativedelta import relativedelta
        for i in range(12):
            month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_start = month_start - relativedelta(months=i)
            month_end = month_start + relativedelta(months=1)
            
            count = self.db.query(Coupon).filter(
                and_(
                    Coupon.campaign_id.isnot(None),
                    Coupon.created_at >= month_start, 
                    Coupon.created_at < month_end
                )
            ).count()
            
            by_month[month_start.strftime("%Y-%m")] = count
        
        return CouponStats(
            total_coupons=total_coupons,
            active_coupons=active_coupons,
            expired_coupons=expired_coupons,
            used_coupons=used_coupons,
            unused_coupons=unused_coupons,
            total_discount_amount=total_discount,
            by_type=by_type,
            by_month=by_month
        )
    
    def delete_coupon(self, coupon_id: int) -> bool:
        """刪除優惠券"""
        coupon = self.get_coupon_by_id(coupon_id)
        if not coupon:
            return False
        
        # 檢查是否已被使用
        usage_count = self.db.query(CouponUsage).filter(CouponUsage.coupon_id == coupon_id).count()
        if usage_count > 0:
            raise ValueError("無法刪除已使用的優惠券")
        
        self.db.delete(coupon)
        self.db.commit()
        return True 