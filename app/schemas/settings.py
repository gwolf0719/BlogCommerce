from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime


class SystemSettingBase(BaseModel):
    key: str = Field(..., description="設定鍵名")
    value: Optional[str] = Field(None, description="設定值")
    description: Optional[str] = Field(None, description="設定描述")
    category: str = Field("general", description="設定分類")
    data_type: str = Field("string", description="數據類型")
    is_public: bool = Field(False, description="是否允許前端訪問")


class SystemSettingCreate(SystemSettingBase):
    pass


class SystemSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    data_type: Optional[str] = None
    is_public: Optional[bool] = None


class SystemSettingResponse(SystemSettingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SystemSettingBulkUpdate(BaseModel):
    settings: Dict[str, Any] = Field(..., description="批量更新的設定")


class FeatureSettings(BaseModel):
    blog_enabled: bool = Field(True, description="是否啟用部落格功能")
    shop_enabled: bool = Field(True, description="是否啟用商店功能")
    comment_enabled: bool = Field(True, description="是否啟用評論功能")
    analytics_enabled: bool = Field(True, description="是否啟用分析功能")
    search_enabled: bool = Field(True, description="是否啟用搜尋功能")
    newsletter_enabled: bool = Field(False, description="是否啟用電子報功能")


class GeneralSettings(BaseModel):
    site_name: str = Field("BlogCommerce", description="網站名稱")
    site_description: str = Field("部落格與電商整合平台", description="網站描述")
    site_keywords: str = Field("電商,部落格,購物", description="網站關鍵字")
    maintenance_mode: bool = Field(False, description="維護模式")
    registration_enabled: bool = Field(True, description="是否允許註冊")


class SeoSettings(BaseModel):
    meta_title: str = Field("BlogCommerce", description="預設 Meta Title")
    meta_description: str = Field("部落格與電商整合平台", description="預設 Meta Description")
    meta_keywords: str = Field("電商,部落格,購物", description="預設 Meta Keywords")
    google_analytics_id: str = Field("", description="Google Analytics ID")
    google_tag_manager_id: str = Field("", description="Google Tag Manager ID")


class EcommerceSettings(BaseModel):
    currency: str = Field("TWD", description="預設貨幣")
    currency_symbol: str = Field("NT$", description="貨幣符號")
    tax_rate: float = Field(0.05, description="稅率")
    payment_methods: List[str] = Field(["credit_card", "bank_transfer"], description="支付方式")


class SystemSettingsGroup(BaseModel):
    features: FeatureSettings
    general: GeneralSettings
    seo: SeoSettings
    ecommerce: EcommerceSettings 

# 金流設定相關 Schema
class PaymentTransferSettings(BaseModel):
    bank_name: str = Field(..., description="銀行名稱")
    account_number: str = Field(..., description="銀行帳號")
    account_name: str = Field(..., description="戶名")

class PaymentLinePaySettings(BaseModel):
    channel_id: str = Field(..., description="Channel ID")
    channel_secret: str = Field(..., description="Channel Secret")
    
class PaymentECPaySettings(BaseModel):
    merchant_id: str = Field(..., description="商店代號")
    hash_key: str = Field(..., description="HashKey")
    hash_iv: str = Field(..., description="HashIV")

class PaymentPayPalSettings(BaseModel):
    client_id: str = Field(..., description="Client ID")
    client_secret: str = Field(..., description="Client Secret")
    environment: str = Field("sandbox", description="環境 (sandbox/live)")

# 用於後端 API 的新 Schema
class PaymentTransferDetails(BaseModel):
    bank: str = ""
    account: str = ""
    name: str = ""

class PaymentLinePayDetails(BaseModel):
    channel_id: str = ""
    channel_secret: str = ""
    store_name: str = ""

class PaymentECPayDetails(BaseModel):
    merchant_id: str = ""
    hash_key: str = ""
    hash_iv: str = ""
    api_url: str = ""

class PaymentPayPalDetails(BaseModel):
    client_id: str = ""
    client_secret: str = ""
    environment: str = "sandbox"

class AllPaymentSettingsResponse(BaseModel):
    enabledMethods: List[str]
    transfer: PaymentTransferDetails
    linepay: PaymentLinePayDetails
    ecpay: PaymentECPayDetails
    paypal: PaymentPayPalDetails

class AllPaymentSettingsUpdate(BaseModel):
    enabledMethods: List[str]
    transfer: PaymentTransferDetails
    linepay: PaymentLinePayDetails
    ecpay: PaymentECPayDetails
    paypal: PaymentPayPalDetails 