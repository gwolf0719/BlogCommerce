from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.discount_code import PromoCode, PromoType
from app.models.discount_usage import PromoUsage
from app.models.order import Order
from app.models.user import User
from app.schemas.discount_code import (
    PromoCodeCreate, PromoCodeUpdate, PromoCodeValidateRequest,
    PromoCodeValidateResponse, PromoCodeStatsResponse
)
import logging

logger = logging.getLogger(__name__)


class PromoService:
    """推薦碼服務層"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_promo_code(self, promo_data: PromoCodeCreate) -> PromoCode:
        """建立推薦碼"""
        try:
            # 檢查推薦碼是否已存在
            existing_code = self.db.query(PromoCode).filter(
                PromoCode.code == promo_data.code.upper()
            ).first()
            
            if existing_code:
                raise ValueError(f"推薦碼 '{promo_data.code}' 已存在")
            
            # 建立新的推薦碼
            promo_code = PromoCode(
                code=promo_data.code.upper(),
                name=promo_data.name,
                source=promo_data.source,
                promo_type=promo_data.promo_type,
                promo_value=promo_data.promo_value,
                start_date=promo_data.start_date,
                end_date=promo_data.end_date,
                usage_limit=promo_data.usage_limit,
                min_order_amount=promo_data.min_order_amount,
                is_active=promo_data.is_active,
                description=promo_data.description
            )
            
            self.db.add(promo_code)
            self.db.commit()
            self.db.refresh(promo_code)
            
            logger.info(f"已建立推薦碼: {promo_code.code}")
            return promo_code
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"建立推薦碼失敗: {str(e)}")
            raise
    
    def get_promo_codes(self, skip: int = 0, limit: int = 100, 
                       is_active: Optional[bool] = None) -> List[PromoCode]:
        """
        取得推薦碼列表
        """
        query = self.db.query(PromoCode)
        
        if is_active is not None:
            query = query.filter(PromoCode.is_active == is_active)
        
        result = query.offset(skip).limit(limit).all()
        return result if result is not None else []
    
    def get_promo_code_by_id(self, promo_code_id: int) -> Optional[PromoCode]:
        """根據ID取得推薦碼"""
        return self.db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()
    
    def get_promo_code_by_code(self, code: str) -> Optional[PromoCode]:
        """根據代碼取得推薦碼"""
        return self.db.query(PromoCode).filter(PromoCode.code == code.upper()).first()
    
    def update_promo_code(self, promo_code_id: int, promo_data: PromoCodeUpdate) -> Optional[PromoCode]:
        """更新推薦碼"""
        try:
            promo_code = self.get_promo_code_by_id(promo_code_id)
            if not promo_code:
                return None
            
            # 更新欄位
            update_data = promo_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == 'code' and value:
                    value = value.upper()
                setattr(promo_code, field, value)
            
            self.db.commit()
            self.db.refresh(promo_code)
            
            logger.info(f"已更新推薦碼: {promo_code.code}")
            return promo_code
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新推薦碼失敗: {str(e)}")
            raise
    
    def delete_promo_code(self, promo_code_id: int) -> bool:
        """刪除推薦碼"""
        try:
            promo_code = self.get_promo_code_by_id(promo_code_id)
            if not promo_code:
                return False
            
            # 檢查是否有使用記錄
            usage_count = self.db.query(PromoUsage).filter(
                PromoUsage.promo_code_id == promo_code_id
            ).count()
            
            if usage_count > 0:
                raise ValueError("無法刪除已被使用的推薦碼")
            
            self.db.delete(promo_code)
            self.db.commit()
            
            logger.info(f"已刪除推薦碼: {promo_code.code}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"刪除推薦碼失敗: {str(e)}")
            raise
    
    def validate_promo_code(self, code: str, order_amount: Decimal) -> Dict[str, Any]:
        """
        驗證推薦碼
        """
        try:
            promo_code = self.get_promo_code_by_code(code)
            
            if not promo_code:
                return {
                    "is_valid": False,
                    "promo_amount": Decimal("0"),
                    "message": "推薦碼不存在",
                    "promo_code": None
                }
            
            if hasattr(promo_code, 'is_active') and promo_code.is_active != True:
                return {
                    "is_valid": False,
                    "promo_amount": Decimal("0"),
                    "message": "推薦碼已停用",
                    "promo_code": None
                }
            # 檢查時間範圍
            now = datetime.now()
            if promo_code.start_date is not None and promo_code.start_date > now:
                return {
                    "is_valid": False,
                    "promo_amount": Decimal("0"),
                    "message": "推薦碼尚未開始",
                    "promo_code": None
                }
            if promo_code.end_date is not None and promo_code.end_date < now:
                return {
                    "is_valid": False,
                    "promo_amount": Decimal("0"),
                    "message": "推薦碼已過期",
                    "promo_code": None
                }
            # 檢查使用次數限制
            if promo_code.usage_limit is not None and promo_code.used_count is not None and promo_code.used_count >= promo_code.usage_limit:
                return {
                    "is_valid": False,
                    "promo_amount": Decimal("0"),
                    "message": "推薦碼已達使用次數上限",
                    "promo_code": None
                }
            # 檢查最小訂單金額
            if promo_code.min_order_amount is not None and order_amount < Decimal(str(promo_code.min_order_amount)):
                return {
                    "is_valid": False,
                    "promo_amount": Decimal("0"),
                    "message": f"訂單金額需達到 NT${promo_code.min_order_amount} 才能使用此推薦碼",
                    "promo_code": None
                }
            
            # 計算推薦金額
            promo_amount = self._calculate_promo_amount(promo_code, order_amount)
            
            return {
                "is_valid": True,
                "promo_amount": promo_amount,
                "message": "推薦碼驗證成功",
                "promo_code": promo_code
            }
            
        except Exception as e:
            logger.error(f"驗證推薦碼失敗: {str(e)}")
            return {
                "is_valid": False,
                "promo_amount": Decimal("0"),
                "message": "驗證失敗",
                "promo_code": None
            }

    def _calculate_promo_amount(self, promo_code: PromoCode, order_amount: Decimal) -> Decimal:
        """
        計算推薦金額
        """
        if promo_code.promo_type == PromoType.PERCENTAGE:
            # 百分比推薦
            promo_amount = order_amount * (Decimal(str(promo_code.promo_value)) / Decimal("100"))
            # 將百分比推薦四捨五入到整數
            return Decimal(str(round(float(promo_amount))))
        elif promo_code.promo_type == PromoType.AMOUNT:
            # 固定金額推薦
            return min(Decimal(str(promo_code.promo_value)), order_amount)
        elif promo_code.promo_type == PromoType.FREE_SHIPPING:
            # 免運費（這裡返回0，實際免運邏輯在訂單處理中處理）
            return Decimal("0")
        else:
            return Decimal("0")
    
    def get_promo_usage_history(self, promo_code_id: int, skip: int = 0, 
                               limit: int = 100) -> List[PromoUsage]:
        """取得推薦碼使用記錄"""
        return self.db.query(PromoUsage).filter(
            PromoUsage.promo_code_id == promo_code_id
        ).offset(skip).limit(limit).all()
    
    def get_promo_stats(self) -> Dict[str, Any]:
        """取得推薦碼統計資料"""
        try:
            # 基本統計
            total_codes = self.db.query(PromoCode).count()
            active_codes = self.db.query(PromoCode).filter(PromoCode.is_active == True).count()
            
            # 使用統計
            total_usage = self.db.query(PromoUsage).count()
            total_promo_amount = self.db.query(func.sum(PromoUsage.promo_amount)).scalar() or Decimal("0")
            
            # 最熱門推薦碼
            most_used_query = self.db.query(
                PromoCode.code,
                func.count(PromoUsage.id).label('usage_count')
            ).outerjoin(
                PromoUsage, PromoCode.id == PromoUsage.promo_code_id
            ).group_by(PromoCode.code).order_by(
                func.count(PromoUsage.id).desc()
            ).first()
            
            most_used_code = most_used_query.code if most_used_query else None
            most_used_count = most_used_query.usage_count if most_used_query else 0
            
            return {
                "total_codes": total_codes,
                "active_codes": active_codes,
                "total_usage": total_usage,
                "total_promo_amount": float(total_promo_amount),
                "most_used_code": most_used_code,
                "most_used_count": most_used_count
            }
            
        except Exception as e:
            logger.error(f"取得推薦碼統計失敗: {str(e)}")
            raise


# 向後相容的別名
DiscountService = PromoService 