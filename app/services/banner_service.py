from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.models.banner import Banner, BannerPosition
from app.schemas.banner import BannerCreate, BannerUpdate, BannerStats
from sqlalchemy import and_, func, desc, asc


class BannerService:
    """
    廣告服務類別
    
    提供廣告相關的業務邏輯處理，包括：
    - 廣告的 CRUD 操作
    - 廣告狀態管理
    - 廣告統計分析
    - 廣告點擊追蹤
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_banner(self, banner_data: BannerCreate) -> Banner:
        """
        建立新廣告
        
        Args:
            banner_data: 廣告建立資料
            
        Returns:
            Banner: 建立的廣告物件
            
        Raises:
            HTTPException: 當建立失敗時
        """
        try:
            # 建立廣告物件
            banner = Banner(**banner_data.model_dump())
            
            # 加入資料庫
            self.db.add(banner)
            self.db.commit()
            self.db.refresh(banner)
            
            return banner
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"建立廣告失敗: {str(e)}"
            )
    
    def get_banner_by_id(self, banner_id: int) -> Optional[Banner]:
        """
        透過 ID 取得廣告
        
        Args:
            banner_id: 廣告 ID
            
        Returns:
            Optional[Banner]: 廣告物件或 None
        """
        return self.db.query(Banner).filter(Banner.id == banner_id).first()
    
    def get_banners(
        self, 
        skip: int = 0,
        limit: int = 100,
        position: Optional[BannerPosition] = None,
        is_active: Optional[bool] = None,
        is_displayable: Optional[bool] = None
    ) -> List[Banner]:
        """
        取得廣告列表
        
        Args:
            skip: 跳過的項目數
            limit: 限制項目數
            position: 版位篩選
            is_active: 啟用狀態篩選
            is_displayable: 是否可顯示篩選
            
        Returns:
            List[Banner]: 廣告列表
        """
        query = self.db.query(Banner)
        
        # 版位篩選
        if position:
            query = query.filter(Banner.position == position)
        
        # 啟用狀態篩選
        if is_active is not None:
            query = query.filter(Banner.is_active == is_active)
        
        # 可顯示狀態篩選（需要同時檢查啟用狀態和時間範圍）
        if is_displayable is not None:
            current_time = datetime.now(timezone.utc)
            if is_displayable:
                query = query.filter(
                    and_(
                        Banner.is_active == True,
                        Banner.start_date <= current_time,
                        Banner.end_date >= current_time
                    )
                )
            else:
                query = query.filter(
                    and_(
                        Banner.is_active == False,
                        Banner.start_date > current_time,
                        Banner.end_date < current_time
                    )
                )
        
        # 排序：按照排序權重降序，然後按建立時間降序
        query = query.order_by(desc(Banner.sort_order), desc(Banner.created_at))
        
        return query.offset(skip).limit(limit).all()
    
    def get_active_banners_by_position(self, position: BannerPosition) -> List[Banner]:
        """
        取得指定版位的所有啟用廣告
        
        Args:
            position: 版位
            
        Returns:
            List[Banner]: 啟用的廣告列表
        """
        current_time = datetime.now(timezone.utc)
        
        return self.db.query(Banner).filter(
            and_(
                Banner.position == position,
                Banner.is_active == True,
                Banner.start_date <= current_time,
                Banner.end_date >= current_time
            )
        ).order_by(desc(Banner.sort_order), desc(Banner.created_at)).all()
    
    def update_banner(self, banner_id: int, banner_data: BannerUpdate) -> Optional[Banner]:
        """
        更新廣告
        
        Args:
            banner_id: 廣告 ID
            banner_data: 更新資料
            
        Returns:
            Optional[Banner]: 更新後的廣告物件或 None
            
        Raises:
            HTTPException: 當更新失敗時
        """
        banner = self.get_banner_by_id(banner_id)
        if not banner:
            return None
        
        try:
            # 更新廣告資料
            update_data = banner_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(banner, field, value)
            
            self.db.commit()
            self.db.refresh(banner)
            
            return banner
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新廣告失敗: {str(e)}"
            )
    
    def delete_banner(self, banner_id: int) -> bool:
        """
        刪除廣告
        
        Args:
            banner_id: 廣告 ID
            
        Returns:
            bool: 是否成功刪除
        """
        banner = self.get_banner_by_id(banner_id)
        if not banner:
            return False
        
        try:
            self.db.delete(banner)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"刪除廣告失敗: {str(e)}"
            )
    
    def toggle_banner_status(self, banner_id: int) -> Optional[Banner]:
        """
        切換廣告狀態
        
        Args:
            banner_id: 廣告 ID
            
        Returns:
            Optional[Banner]: 更新後的廣告物件或 None
        """
        banner = self.get_banner_by_id(banner_id)
        if not banner:
            return None
        
        try:
            # 使用 setattr 來更新屬性
            setattr(banner, 'is_active', not getattr(banner, 'is_active'))
            self.db.commit()
            self.db.refresh(banner)
            
            return banner
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"切換廣告狀態失敗: {str(e)}"
            )
    
    def track_banner_click(self, banner_id: int) -> bool:
        """
        追蹤廣告點擊
        
        Args:
            banner_id: 廣告 ID
            
        Returns:
            bool: 是否成功追蹤
        """
        banner = self.get_banner_by_id(banner_id)
        if not banner:
            return False
        
        try:
            banner.increment_click_count()
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"追蹤廣告點擊失敗: {str(e)}"
            )
    
    def get_banner_stats(self) -> BannerStats:
        """
        取得廣告統計資料
        
        Returns:
            BannerStats: 統計資料
        """
        current_time = datetime.now(timezone.utc)
        
        # 基本統計
        total_banners = self.db.query(Banner).count()
        active_banners = self.db.query(Banner).filter(
            and_(
                Banner.is_active == True,
                Banner.start_date <= current_time,
                Banner.end_date >= current_time
            )
        ).count()
        
        expired_banners = self.db.query(Banner).filter(
            Banner.end_date < current_time
        ).count()
        
        # 總點擊數
        total_clicks = self.db.query(func.sum(Banner.click_count)).scalar() or 0
        
        # 各版位統計
        position_stats = {}
        for position in BannerPosition:
            position_count = self.db.query(Banner).filter(
                Banner.position == position
            ).count()
            
            position_clicks = self.db.query(
                func.sum(Banner.click_count)
            ).filter(
                Banner.position == position
            ).scalar() or 0
            
            position_stats[position.value] = {
                "count": position_count,
                "clicks": position_clicks
            }
        
        return BannerStats(
            total_banners=total_banners,
            active_banners=active_banners,
            expired_banners=expired_banners,
            total_clicks=total_clicks,
            position_stats=position_stats
        )
    
    def get_expired_banners(self) -> List[Banner]:
        """
        取得過期的廣告
        
        Returns:
            List[Banner]: 過期廣告列表
        """
        current_time = datetime.now(timezone.utc)
        
        return self.db.query(Banner).filter(
            Banner.end_date < current_time
        ).order_by(desc(Banner.end_date)).all()
    
    def get_soon_to_expire_banners(self, days: int = 7) -> List[Banner]:
        """
        取得即將過期的廣告
        
        Args:
            days: 天數（預設7天）
            
        Returns:
            List[Banner]: 即將過期的廣告列表
        """
        from datetime import timedelta
        
        current_time = datetime.now(timezone.utc)
        future_time = current_time + timedelta(days=days)
        
        return self.db.query(Banner).filter(
            and_(
                Banner.end_date > current_time,
                Banner.end_date <= future_time,
                Banner.is_active == True
            )
        ).order_by(asc(Banner.end_date)).all() 