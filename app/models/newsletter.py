from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    source = Column(String(50), default="website", nullable=False)  # website, admin, import
    tags = Column(Text, nullable=True)  # JSON string for categorization
    unsubscribe_token = Column(String(255), unique=True, nullable=True)
    last_email_sent = Column(DateTime(timezone=True), nullable=True)
    
    # 統計資料
    emails_sent = Column(Integer, default=0, nullable=False)
    emails_opened = Column(Integer, default=0, nullable=False)
    emails_clicked = Column(Integer, default=0, nullable=False)
    
    # 時間戳
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 確保每個 email 只能有一個有效訂閱
    __table_args__ = (
        UniqueConstraint('email', name='unique_email'),
    )
    
    def __repr__(self):
        return f"<NewsletterSubscriber(email='{self.email}', is_active={self.is_active})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "source": self.source,
            "tags": self.tags,
            "emails_sent": self.emails_sent,
            "emails_opened": self.emails_opened,
            "emails_clicked": self.emails_clicked,
            "subscribed_at": self.subscribed_at.isoformat() if self.subscribed_at else None,
            "unsubscribed_at": self.unsubscribed_at.isoformat() if self.unsubscribed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class NewsletterCampaign(Base):
    __tablename__ = "newsletter_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)
    
    # 發送設定
    status = Column(String(20), default="draft", nullable=False)  # draft, scheduled, sending, sent, cancelled
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # 統計資料
    recipients_count = Column(Integer, default=0, nullable=False)
    delivered_count = Column(Integer, default=0, nullable=False)
    opened_count = Column(Integer, default=0, nullable=False)
    clicked_count = Column(Integer, default=0, nullable=False)
    bounced_count = Column(Integer, default=0, nullable=False)
    unsubscribed_count = Column(Integer, default=0, nullable=False)
    
    # 時間戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NewsletterCampaign(title='{self.title}', status='{self.status}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subject": self.subject,
            "content": self.content,
            "html_content": self.html_content,
            "status": self.status,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "recipients_count": self.recipients_count,
            "delivered_count": self.delivered_count,
            "opened_count": self.opened_count,
            "clicked_count": self.clicked_count,
            "bounced_count": self.bounced_count,
            "unsubscribed_count": self.unsubscribed_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 