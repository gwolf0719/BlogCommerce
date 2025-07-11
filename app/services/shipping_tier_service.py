from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from fastapi import HTTPException, status
from app.models.shipping_tier import ShippingTier
from app.schemas.shipping_tier import ShippingTierCreate, ShippingTierUpdate, ShippingTierStats
from sqlalchemy import and_, func, desc, asc


class ShippingTierService:
    """
    運費級距服務類別
    
    提供運費級距相關的業務邏輯處理，包括：
    - 運費級距的 CRUD 操作
    - 運費計算邏輯
    - 級距統計分析
    - 級距衝突檢查
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_shipping_tier(self, tier_data: ShippingTierCreate) -> ShippingTier:
        """
        建立新運費級距
        
        Args:
            tier_data: 運費級距建立資料
            
        Returns:
            ShippingTier: 建立的運費級距物件
            
        Raises:
            HTTPException: 當建立失敗或存在衝突時
        """
        # 檢查是否與現有級距衝突
        conflict_tier = self._check_tier_conflict(
            tier_data.min_amount, 
            tier_data.max_amount
        )
        
        if conflict_tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"運費級距範圍與現有級距 '{conflict_tier.name}' 衝突"
            )
        
        try:
            # 建立運費級距物件
            tier = ShippingTier(**tier_data.model_dump())
            
            # 加入資料庫
            self.db.add(tier)
            self.db.commit()
            self.db.refresh(tier)
            
            return tier
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"建立運費級距失敗: {str(e)}"
            )
    
    def get_shipping_tier_by_id(self, tier_id: int) -> Optional[ShippingTier]:
        """
        透過 ID 取得運費級距
        
        Args:
            tier_id: 運費級距 ID
            
        Returns:
            Optional[ShippingTier]: 運費級距物件或 None
        """
        return self.db.query(ShippingTier).filter(ShippingTier.id == tier_id).first()
    
    def get_shipping_tiers(
        self, 
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        sort_by_amount: bool = True
    ) -> List[ShippingTier]:
        """
        取得運費級距列表
        
        Args:
            skip: 跳過的項目數
            limit: 限制項目數
            is_active: 啟用狀態篩選
            sort_by_amount: 是否按金額排序（預設按最低金額升序）
            
        Returns:
            List[ShippingTier]: 運費級距列表
        """
        query = self.db.query(ShippingTier)
        
        # 啟用狀態篩選
        if is_active is not None:
            query = query.filter(ShippingTier.is_active == is_active)
        
        # 排序
        if sort_by_amount:
            # 按最低金額升序，然後按排序權重降序
            query = query.order_by(asc(ShippingTier.min_amount), desc(ShippingTier.sort_order))
        else:
            # 按排序權重降序，然後按建立時間降序
            query = query.order_by(desc(ShippingTier.sort_order), desc(ShippingTier.created_at))
        
        return query.offset(skip).limit(limit).all()
    
    def get_active_shipping_tiers(self) -> List[ShippingTier]:
        """
        取得所有啟用的運費級距
        
        Returns:
            List[ShippingTier]: 啟用的運費級距列表，按最低金額升序排列
        """
        return self.db.query(ShippingTier).filter(
            ShippingTier.is_active == True
        ).order_by(asc(ShippingTier.min_amount), desc(ShippingTier.sort_order)).all()
    
    def update_shipping_tier(self, tier_id: int, tier_data: ShippingTierUpdate) -> Optional[ShippingTier]:
        """
        更新運費級距
        
        Args:
            tier_id: 運費級距 ID
            tier_data: 更新資料
            
        Returns:
            Optional[ShippingTier]: 更新後的運費級距物件或 None
            
        Raises:
            HTTPException: 當更新失敗或存在衝突時
        """
        tier = self.get_shipping_tier_by_id(tier_id)
        if not tier:
            return None
        
        # 檢查是否與現有級距衝突（排除自己）
        update_data = tier_data.model_dump(exclude_unset=True)
        if 'min_amount' in update_data or 'max_amount' in update_data:
            min_amount = update_data.get('min_amount', tier.min_amount)
            max_amount = update_data.get('max_amount', tier.max_amount)
            
            conflict_tier = self._check_tier_conflict(min_amount, max_amount, exclude_id=tier_id)
            
            if conflict_tier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"運費級距範圍與現有級距 '{conflict_tier.name}' 衝突"
                )
        
        try:
            # 更新運費級距資料
            for field, value in update_data.items():
                setattr(tier, field, value)
            
            self.db.commit()
            self.db.refresh(tier)
            
            return tier
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新運費級距失敗: {str(e)}"
            )
    
    def delete_shipping_tier(self, tier_id: int) -> bool:
        """
        刪除運費級距
        
        Args:
            tier_id: 運費級距 ID
            
        Returns:
            bool: 是否成功刪除
        """
        tier = self.get_shipping_tier_by_id(tier_id)
        if not tier:
            return False
        
        try:
            self.db.delete(tier)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"刪除運費級距失敗: {str(e)}"
            )
    
    def toggle_tier_status(self, tier_id: int) -> Optional[ShippingTier]:
        """
        切換運費級距啟用狀態
        
        Args:
            tier_id: 運費級距 ID
            
        Returns:
            Optional[ShippingTier]: 更新後的運費級距物件或 None
        """
        tier = self.get_shipping_tier_by_id(tier_id)
        if not tier:
            return None
        
        try:
            # 正確的方式來切換布爾值
            current_status = tier.is_active
            tier.is_active = not current_status
            self.db.commit()
            self.db.refresh(tier)
            
            return tier
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"切換運費級距狀態失敗: {str(e)}"
            )
    
    def calculate_shipping_fee(self, order_amount: Decimal) -> Tuple[Decimal, bool, Optional[ShippingTier], str]:
        """
        計算指定訂單金額的運費
        
        Args:
            order_amount: 訂單金額
            
        Returns:
            Tuple[Decimal, bool, Optional[ShippingTier], str]: 
            (運費金額, 是否免運費, 適用級距, 說明訊息)
        """
        # 取得所有啟用的運費級距
        active_tiers = self.get_active_shipping_tiers()
        
        if not active_tiers:
            return Decimal('0'), True, None, "系統尚未設定運費級距，免運費"
        
        # 尋找適用的級距
        applicable_tier = None
        for tier in active_tiers:
            if tier.applies_to_amount(order_amount):
                applicable_tier = tier
                break
        
        if not applicable_tier:
            # 找不到適用級距，使用最後一個級距（最高金額級距）
            last_tier = active_tiers[-1]
            if last_tier.is_unlimited_max or order_amount >= last_tier.min_amount:
                applicable_tier = last_tier
        
        if not applicable_tier:
            return Decimal('0'), True, None, f"訂單金額 ${order_amount} 找不到適用的運費級距，免運費"
        
        shipping_fee = applicable_tier.get_shipping_cost()
        is_free = applicable_tier.free_shipping or shipping_fee == 0
        
        if is_free:
            message = f"適用級距：{applicable_tier.name}，免運費"
        else:
            message = f"適用級距：{applicable_tier.name}，運費 ${shipping_fee}"
        
        return shipping_fee, is_free, applicable_tier, message
    
    def calculate_detailed_shipping_fee(self, order_amount: Decimal) -> Tuple[Decimal, bool, Optional[ShippingTier], str, Optional[Decimal], Optional[Decimal], Optional[Decimal], Optional[ShippingTier]]:
        """
        計算詳細的運費資訊
        
        Args:
            order_amount: 訂單金額
            
        Returns:
            Tuple[Decimal, bool, Optional[ShippingTier], str, Optional[Decimal], Optional[Decimal], Optional[Decimal], Optional[ShippingTier]]: 
            (運費金額, 是否免運費, 適用級距, 說明訊息, 最高運費, 免運費門檻, 還需要多少錢才能免運費, 下一個級距)
        """
        # 取得所有啟用的運費級距
        active_tiers = self.get_active_shipping_tiers()
        
        if not active_tiers:
            return Decimal('0'), True, None, "系統尚未設定運費級距，免運費", None, None, None, None
        
        # 尋找適用的級距
        applicable_tier = None
        for tier in active_tiers:
            if tier.applies_to_amount(order_amount):
                applicable_tier = tier
                break
        
        if not applicable_tier:
            # 找不到適用級距，使用最後一個級距（最高金額級距）
            last_tier = active_tiers[-1]
            if last_tier.is_unlimited_max or order_amount >= last_tier.min_amount:
                applicable_tier = last_tier
        
        if not applicable_tier:
            return Decimal('0'), True, None, f"訂單金額 ${order_amount} 找不到適用的運費級距，免運費", None, None, None, None
        
        shipping_fee = applicable_tier.get_shipping_cost()
        is_free = applicable_tier.free_shipping or shipping_fee == 0
        
        # 計算最高運費（找到最高的運費金額）
        max_shipping_fee = None
        max_fee = Decimal('0')
        for tier in active_tiers:
            if not tier.free_shipping and tier.shipping_fee > max_fee:
                max_fee = tier.shipping_fee
                max_shipping_fee = tier.shipping_fee
        
        # 尋找免運費門檻
        free_shipping_threshold = None
        free_shipping_tier = None
        for tier in active_tiers:
            if tier.free_shipping:
                if free_shipping_threshold is None or tier.min_amount < free_shipping_threshold:
                    free_shipping_threshold = tier.min_amount
                    free_shipping_tier = tier
        
        # 計算還需要多少錢才能免運費
        amount_needed_for_free_shipping = None
        if free_shipping_threshold is not None and order_amount < free_shipping_threshold:
            amount_needed_for_free_shipping = free_shipping_threshold - order_amount
        
        # 尋找下一個級距
        next_tier = None
        for tier in active_tiers:
            if tier.min_amount > order_amount:
                next_tier = tier
                break
        
        if is_free:
            message = f"適用級距：{applicable_tier.name}，免運費"
        else:
            message = f"適用級距：{applicable_tier.name}，運費 ${shipping_fee}"
        
        return shipping_fee, is_free, applicable_tier, message, max_shipping_fee, free_shipping_threshold, amount_needed_for_free_shipping, next_tier
    
    def get_shipping_tier_stats(self) -> ShippingTierStats:
        """
        取得運費級距統計資訊
        
        Returns:
            ShippingTierStats: 統計資訊
        """
        # 總級距數
        total_tiers = self.db.query(func.count(ShippingTier.id)).scalar()
        
        # 啟用級距數
        active_tiers = self.db.query(func.count(ShippingTier.id)).filter(
            ShippingTier.is_active == True
        ).scalar()
        
        # 停用級距數
        inactive_tiers = total_tiers - active_tiers
        
        # 免運費級距數
        free_shipping_tiers = self.db.query(func.count(ShippingTier.id)).filter(
            and_(
                ShippingTier.is_active == True,
                ShippingTier.free_shipping == True
            )
        ).scalar()
        
        # 平均運費（排除免運費級距）
        avg_shipping_fee = self.db.query(func.avg(ShippingTier.shipping_fee)).filter(
            and_(
                ShippingTier.is_active == True,
                ShippingTier.free_shipping == False
            )
        ).scalar() or Decimal('0')
        
        return ShippingTierStats(
            total_tiers=total_tiers,
            active_tiers=active_tiers,
            inactive_tiers=inactive_tiers,
            free_shipping_tiers=free_shipping_tiers,
            average_shipping_fee=avg_shipping_fee
        )
    
    def _check_tier_conflict(
        self, 
        min_amount: Decimal, 
        max_amount: Optional[Decimal], 
        exclude_id: Optional[int] = None
    ) -> Optional[ShippingTier]:
        """
        檢查運費級距是否與現有級距衝突
        
        Args:
            min_amount: 最低金額
            max_amount: 最高金額
            exclude_id: 排除的級距 ID（用於更新時）
            
        Returns:
            Optional[ShippingTier]: 衝突的級距物件或 None
        """
        query = self.db.query(ShippingTier).filter(ShippingTier.is_active == True)
        
        # 排除指定 ID
        if exclude_id:
            query = query.filter(ShippingTier.id != exclude_id)
        
        # 檢查範圍衝突
        for existing_tier in query.all():
            if self._ranges_overlap(
                min_amount, max_amount,
                existing_tier.min_amount, existing_tier.max_amount
            ):
                return existing_tier
        
        return None
    
    def _ranges_overlap(
        self, 
        min1: Decimal, max1: Optional[Decimal],
        min2: Decimal, max2: Optional[Decimal]
    ) -> bool:
        """
        檢查兩個金額範圍是否重疊
        
        Args:
            min1, max1: 第一個範圍（min1 包含，max1 不包含，None 表示無上限）
            min2, max2: 第二個範圍（min2 包含，max2 不包含，None 表示無上限）
            
        Returns:
            bool: 是否重疊
        """
        # 如果兩個範圍都有上限
        if max1 is not None and max2 is not None:
            return not (max1 <= min2 or max2 <= min1)
        
        # 如果第一個範圍無上限
        if max1 is None and max2 is not None:
            return min1 < max2
        
        # 如果第二個範圍無上限
        if max1 is not None and max2 is None:
            return min2 < max1
        
        # 如果兩個範圍都無上限，一定重疊
        return True 