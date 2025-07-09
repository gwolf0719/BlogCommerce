from pydantic import BaseModel, ConfigDict, Field, field_serializer
from datetime import datetime
from typing import Optional


class BaseSchema(BaseModel):
    """
    基礎 Schema 類別
    
    提供所有 Pydantic 模型的基本配置，包括：
    - 支援從 SQLAlchemy 模型自動轉換屬性
    - 統一的日期時間序列化格式
    - 標準化的模型配置
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class BaseResponseSchema(BaseSchema):
    """
    基礎響應 Schema 類別
    
    用於所有 API 響應的基礎結構，包含：
    - 資源 ID
    - 創建時間
    - 更新時間
    
    所有資源的響應都應該繼承此類別以保持一致性。
    """
    id: int = Field(..., description="資源唯一識別碼")
    created_at: datetime = Field(..., description="資源創建時間")
    updated_at: Optional[datetime] = Field(None, description="資源最後更新時間")
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        """將創建時間序列化為 ISO 8601 格式"""
        return value.isoformat()
    
    @field_serializer('updated_at')
    def serialize_updated_at(self, value: Optional[datetime], _info) -> Optional[str]:
        """將更新時間序列化為 ISO 8601 格式"""
        return value.isoformat() if value else None
    
    model_config = ConfigDict(
        from_attributes=True
    )


class SlugSchema(BaseSchema):
    """
    URL 別名 Schema 類別
    
    用於需要 URL 友好別名的資源，如文章、商品等。
    Slug 通常用於 SEO 友好的 URL 結構。
    """
    slug: Optional[str] = Field(None, description="URL 友好的別名") 