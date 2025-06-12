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
    SeoSettings, EcommerceSettings, SystemSettingsGroup
)
from ..auth import get_current_user, get_current_admin_user

router = APIRouter()
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
            str_value = str(value) if value is not None else None
        
        if setting:
            setting.value = str_value
            if description:
                setting.description = description
            setting.data_type = data_type
            setting.is_public = is_public
        else:
            setting = SystemSettings(
                key=key,
                value=str_value,
                description=description,
                category=category,
                data_type=data_type,
                is_public=is_public
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
@router.get("/api/settings", response_model=List[SystemSettingResponse])
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


@router.get("/api/settings/public")
async def get_public_settings(db: Session = Depends(get_db)):
    """獲取公開設定（不需要認證）"""
    manager = SettingsManager(db)
    return manager.get_public_settings()


@router.get("/api/settings/{key}")
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


@router.post("/api/settings", response_model=SystemSettingResponse)
async def create_setting(
    setting_data: SystemSettingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """創建新設定"""
    # 檢查是否已存在
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


@router.put("/api/settings/{key}", response_model=SystemSettingResponse)
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


@router.delete("/api/settings/{key}")
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


@router.post("/api/settings/bulk-update")
async def bulk_update_settings(
    data: SystemSettingBulkUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """批量更新設定"""
    manager = SettingsManager(db)
    
    for key, value in data.settings.items():
        # 根據鍵名推斷類別
        if key.startswith("blog_") or key.startswith("shop_") or key.endswith("_enabled"):
            category = "features"
        elif key.startswith("meta_") or key.startswith("google_"):
            category = "seo"
        elif key.startswith("currency") or key.startswith("shipping") or key.startswith("tax"):
            category = "ecommerce"
        else:
            category = "general"
        
        # 設定是否公開（功能開關需要公開）
        is_public = key.endswith("_enabled") or key in ["blog_enabled", "shop_enabled"]
        
        manager.set_setting(key, value, category=category, is_public=is_public)
    
    return {"message": "設定已更新"}


@router.get("/api/settings/features")
async def get_feature_settings(db: Session = Depends(get_db)):
    """獲取功能設定（公開 API）"""
    manager = SettingsManager(db)
    return FeatureSettings(
        blog_enabled=manager.get_setting("blog_enabled", True),
        shop_enabled=manager.get_setting("shop_enabled", True),
        comment_enabled=manager.get_setting("comment_enabled", True),
        analytics_enabled=manager.get_setting("analytics_enabled", True),
        search_enabled=manager.get_setting("search_enabled", True),
        newsletter_enabled=manager.get_setting("newsletter_enabled", False)
    )


@router.put("/api/settings/features")
async def update_feature_settings(
    features: FeatureSettings,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """更新功能設定"""
    manager = SettingsManager(db)
    
    # 更新功能設定
    for key, value in features.dict().items():
        manager.set_setting(
            key, value, 
            category="features", 
            description=f"功能開關：{key}",
            is_public=True
        )
    
    return {"message": "功能設定已更新"}


@router.get("/api/settings/ai")
async def get_ai_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """獲取AI設定"""
    manager = SettingsManager(db)
    ai_settings = manager.get_category_settings("ai")
    
    # 設定預設值
    defaults = {
        "ai_enabled": False,
        "ai_api_provider": "openai",
        "ai_api_key": "",
        "ai_api_url": "https://api.openai.com/v1",
        "ai_text_model": "gpt-3.5-turbo",
        "ai_image_enabled": False,
        "ai_image_model": "dall-e-3",
        "ai_global_prompt": "你是一個專業的部落格文章寫手，請根據用戶提供的主題和要求，撰寫高質量的中文部落格文章。文章應該結構清晰、內容豐富、語言流暢，並符合SEO最佳實踐。",
        "ai_max_tokens": 2000,
        "ai_temperature": 0.7
    }
    
    for key, default_value in defaults.items():
        if key not in ai_settings:
            ai_settings[key] = default_value
    
    return ai_settings


@router.put("/api/settings/ai")
async def update_ai_settings(
    ai_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """更新AI設定"""
    manager = SettingsManager(db)
    
    # 更新AI設定
    for key, value in ai_data.items():
        if key.startswith("ai_"):
            # 根據鍵名推斷描述
            descriptions = {
                "ai_enabled": "啟用AI文章生成功能",
                "ai_api_provider": "AI服務提供商",
                "ai_api_key": "AI API金鑰",
                "ai_api_url": "AI API基礎URL",
                "ai_text_model": "文字生成模型",
                "ai_image_enabled": "啟用AI圖片生成",
                "ai_image_model": "圖片生成模型",
                "ai_global_prompt": "全站AI生成風格提示詞",
                "ai_max_tokens": "AI生成最大token數",
                "ai_temperature": "AI生成創意度(0-1)"
            }
            
            manager.set_setting(
                key, value,
                category="ai",
                description=descriptions.get(key, f"AI設定：{key}"),
                is_public=False
            )
    
    return {"message": "AI設定已更新"}


@router.post("/api/ai/models")
async def get_ai_models(
    data: Dict[str, Any],
    current_user = Depends(get_current_admin_user)
):
    """根據提供商與API路徑取得模型列表"""
    provider = data.get("provider", "openai")
    api_url = data.get("api_url", "https://api.openai.com/v1")
    api_key = data.get("api_key", "")

    from app.services.ai_service import AIService

    async with AIService() as service:
        try:
            models = await service.fetch_available_models(provider, api_url, api_key)
            return {"models": models}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# 管理後台頁面路由（認證由前端JavaScript處理）
@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """設定管理頁面 (前端SPA 渲染)"""
    return FileResponse("app/static/index.html") 