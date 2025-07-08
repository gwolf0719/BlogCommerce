from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class NewsletterSubscriberBase(BaseModel):
    email: EmailStr = Field(..., description="電子郵件地址")
    name: Optional[str] = Field(None, max_length=100, description="姓名")
    source: str = Field("website", description="訂閱來源")
    tags: Optional[str] = Field(None, description="標籤（JSON格式）")


class NewsletterSubscriberCreate(NewsletterSubscriberBase):
    pass


class NewsletterSubscriberUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    tags: Optional[str] = None


class NewsletterSubscriberResponse(NewsletterSubscriberBase):
    id: int
    is_active: bool
    emails_sent: int
    emails_opened: int
    emails_clicked: int
    subscribed_at: datetime
    unsubscribed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NewsletterSubscriptionRequest(BaseModel):
    email: EmailStr = Field(..., description="電子郵件地址")
    name: Optional[str] = Field(None, max_length=100, description="姓名（可選）")


class NewsletterUnsubscribeRequest(BaseModel):
    email: EmailStr = Field(..., description="電子郵件地址")
    token: Optional[str] = Field(None, description="取消訂閱令牌")


class NewsletterCampaignBase(BaseModel):
    title: str = Field(..., max_length=255, description="活動標題")
    subject: str = Field(..., max_length=255, description="郵件主旨")
    content: str = Field(..., description="郵件內容")
    html_content: Optional[str] = Field(None, description="HTML內容")


class NewsletterCampaignCreate(NewsletterCampaignBase):
    scheduled_at: Optional[datetime] = Field(None, description="排程發送時間")


class NewsletterCampaignUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    subject: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    html_content: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None


class NewsletterCampaignResponse(NewsletterCampaignBase):
    id: int
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    recipients_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    bounced_count: int
    unsubscribed_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NewsletterStats(BaseModel):
    total_subscribers: int
    active_subscribers: int
    inactive_subscribers: int
    total_campaigns: int
    sent_campaigns: int
    draft_campaigns: int
    total_emails_sent: int
    total_opens: int
    total_clicks: int
    average_open_rate: float
    average_click_rate: float 