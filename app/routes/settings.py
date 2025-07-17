from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from ..database import get_db
from ..models.settings import SystemSettings
from ..schemas.settings import (
    SystemSettingResponse, SystemSettingCreate, SystemSettingUpdate,
    SystemSettingBulkUpdate, FeatureSettings, GeneralSettings,
    SeoSettings, EcommerceSettings, SystemSettingsGroup,
    AllPaymentSettingsResponse, AllPaymentSettingsUpdate,
    PaymentTransferDetails, PaymentLinePayDetails, PaymentECPayDetails, PaymentPayPalDetails
)
from ..auth import get_current_user, get_current_admin_user

router = APIRouter(tags=["系統設定"])

# 將管理員設定 API 掛載到 /admin/settings
admin_router = APIRouter(prefix="/admin/settings", tags=["系統設定"])

# 將公開設定 API 掛載到 /settings
public_router = APIRouter(prefix="/settings", tags=["系統設定"])
templates = Jinja2Templates(directory="app/templates")

# 設定工具類
class SettingsManager:
    def __init__(self, db: Session):
        self.db = db
    
    def get_setting(self, key: str, default=None) -> Any:
        """獲取單個設定值"""
        setting = self.db.query(SystemSettings).filter(SystemSettings.key == key).first()
        if setting:
            return setting.parse_value()
        return default
    
    def set_setting(self, key: str, value: Any, description: str = None, 
                   category: str = "general", data_type: str = "string", 
                   is_public: bool = False) -> SystemSettings:
        """設置單個設定值"""
        setting = self.db.query(SystemSettings).filter(SystemSettings.key == key).first()
        
        # 轉換值為字符串
        if isinstance(value, bool):
            str_value = "true" if value else "false"
            data_type = "boolean"
        elif isinstance(value, (int, float)):
            str_value = str(value)
            data_type = "integer" if isinstance(value, int) else "float"
        elif isinstance(value, (dict, list)):
            str_value = json.dumps(value)
            data_type = "json"
        else:
            str_value = str(value) if value is not None else ""
        
        if setting:
            setting.value = str_value
            setting.description = str(description) if description is not None else ""
            setting.data_type = str(data_type) if data_type is not None else "string"
            setting.category = str(category) if category is not None else "general"
            setting.is_public = bool(is_public)
        else:
            setting = SystemSettings(
                key=str(key),
                value=str_value,
                description=str(description) if description is not None else "",
                category=str(category) if category is not None else "general",
                data_type=str(data_type) if data_type is not None else "string",
                is_public=bool(is_public)
            )
            self.db.add(setting)
        
        self.db.commit()
        self.db.refresh(setting)
        return setting
    
    def get_category_settings(self, category: str) -> Dict[str, Any]:
        """獲取分類下的所有設定"""
        settings = self.db.query(SystemSettings).filter(
            SystemSettings.category == category
        ).all()
        return {setting.key: setting.parse_value() for setting in settings}
    
    def get_public_settings(self) -> Dict[str, Any]:
        """獲取所有公開設定"""
        settings = self.db.query(SystemSettings).filter(
            SystemSettings.is_public == True
        ).all()
        return {setting.key: setting.parse_value() for setting in settings}


# API 路由
@router.get("/settings/", response_model=List[SystemSettingResponse])
@router.get("/settings", response_model=List[SystemSettingResponse])
async def get_all_settings(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """獲取所有系統設定"""
    query = db.query(SystemSettings)
    if category:
        query = query.filter(SystemSettings.category == category)
    
    settings = query.all()
    return [SystemSettingResponse.from_orm(setting) for setting in settings]


@router.get("/settings/public")
async def get_public_settings(db: Session = Depends(get_db)):
    """獲取公開設定（不需要認證）"""
    manager = SettingsManager(db)
    return manager.get_public_settings()


@router.get("/settings/{key}")
async def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """獲取單個設定"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="設定項目不存在")
    return SystemSettingResponse.from_orm(setting)


@router.post("/settings/", response_model=SystemSettingResponse)
@router.post("/settings", response_model=SystemSettingResponse)
async def create_setting(
    setting_data: SystemSettingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """創建新設定"""
    existing = db.query(SystemSettings).filter(
        SystemSettings.key == setting_data.key
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="設定項目已存在")
    
    setting = SystemSettings(**setting_data.dict())
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return SystemSettingResponse.from_orm(setting)


@router.put("/settings/{key}", response_model=SystemSettingResponse)
async def update_setting(
    key: str,
    setting_data: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """更新設定"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="設定項目不存在")
    
    update_data = setting_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)
    
    db.commit()
    db.refresh(setting)
    return SystemSettingResponse.from_orm(setting)


@router.delete("/settings/{key}")
async def delete_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """刪除設定"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="設定項目不存在")
    
    db.delete(setting)
    db.commit()
    return {"message": "設定已刪除"}


@router.post("/settings/bulk-update")
async def bulk_update_settings(
    data: SystemSettingBulkUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """批量更新設定"""
    manager = SettingsManager(db)
    
    for key, value in data.settings.items():
        if key.startswith("blog_") or key.startswith("shop_") or key.endswith("_enabled"):
            category = "features"
        elif key.startswith("meta_") or key.startswith("google_"):
            category = "seo"
        elif key.startswith("currency") or key.startswith("shipping") or key.startswith("tax"):
            category = "ecommerce"
        else:
            category = "general"
        
        is_public = key.endswith("_enabled") or key in ["blog_enabled", "shop_enabled"]
        
        manager.set_setting(key, value, category=category, is_public=is_public)
    
    return {"message": "設定已更新"}

# --- 金流設定 ---
@router.get("/admin/payment/settings", response_model=AllPaymentSettingsResponse)
async def get_all_payment_settings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """獲取所有金流設定（管理員）"""
    manager = SettingsManager(db)
    
    enabled_methods = []
    if manager.get_setting("payment_transfer_enabled", False):
        enabled_methods.append("transfer")
    if manager.get_setting("payment_linepay_enabled", False):
        enabled_methods.append("linepay")
    if manager.get_setting("payment_ecpay_enabled", False):
        enabled_methods.append("ecpay")
    if manager.get_setting("payment_paypal_enabled", False):
        enabled_methods.append("paypal")

    return AllPaymentSettingsResponse(
        enabledMethods=enabled_methods,
        transfer=manager.get_setting("payment_transfer_details", {}),
        linepay=manager.get_setting("payment_linepay_details", {}),
        ecpay=manager.get_setting("payment_ecpay_details", {}),
        paypal=manager.get_setting("payment_paypal_details", {})
    )

@router.put("/admin/payment/settings")
async def update_all_payment_settings(
    settings_data: AllPaymentSettingsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """更新所有金流設定（管理員）"""
    manager = SettingsManager(db)

    # 更新啟用狀態
    manager.set_setting("payment_transfer_enabled", "transfer" in settings_data.enabledMethods, category="payment", is_public=True)
    manager.set_setting("payment_linepay_enabled", "linepay" in settings_data.enabledMethods, category="payment", is_public=True)
    manager.set_setting("payment_ecpay_enabled", "ecpay" in settings_data.enabledMethods, category="payment", is_public=True)
    manager.set_setting("payment_paypal_enabled", "paypal" in settings_data.enabledMethods, category="payment", is_public=True)

    # 更新詳細設定
    manager.set_setting("payment_transfer_details", settings_data.transfer.dict(), category="payment", data_type="json")
    manager.set_setting("payment_linepay_details", settings_data.linepay.dict(), category="payment", data_type="json")
    manager.set_setting("payment_ecpay_details", settings_data.ecpay.dict(), category="payment", data_type="json")
    manager.set_setting("payment_paypal_details", settings_data.paypal.dict(), category="payment", data_type="json")

    return {"message": "金流設定已成功更新"}


# --- 公開金流 API ---
@router.get("/settings/payment/settings")
async def get_public_payment_settings(db: Session = Depends(get_db)):
    """獲取已啟用的付款方式設定（公開端點，供前台使用）"""
    manager = SettingsManager(db)
    
    settings = {}
    # 轉帳
    if manager.get_setting("payment_transfer_enabled", False):
        details = manager.get_setting("payment_transfer_details", {})
        if details and details.get("bank") and details.get("account") and details.get("name"):
            settings["transfer"] = {"enabled": True, "details": details}
        else:
            # 如果啟用但未配置，可以選擇不回傳或標記為未配置
            settings["transfer"] = {"enabled": True, "configured": False}

    # LinePay
    if manager.get_setting("payment_linepay_enabled", False):
        details = manager.get_setting("payment_linepay_details", {})
        if details and details.get("channel_id"):
             settings["linepay"] = {"enabled": True} # Secret 不應傳到前端
        else:
             settings["linepay"] = {"enabled": True, "configured": False}

    # ECPay
    if manager.get_setting("payment_ecpay_enabled", False):
        details = manager.get_setting("payment_ecpay_details", {})
        if details and details.get("merchant_id"):
            settings["ecpay"] = {"enabled": True}
        else:
            settings["ecpay"] = {"enabled": True, "configured": False}

    # PayPal
    if manager.get_setting("payment_paypal_enabled", False):
        details = manager.get_setting("payment_paypal_details", {})
        if details and details.get("client_id"):
            settings["paypal"] = {"enabled": True}
        else:
            settings["paypal"] = {"enabled": True, "configured": False}
            
    return settings

# 管理後台頁面路由
@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """設定管理頁面 (前端SPA 渲染)"""
    return FileResponse("app/static/index.html")
 