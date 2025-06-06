from pydantic import BaseModel, ConfigDict, Field, field_serializer
from datetime import datetime
from typing import Optional


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class BaseResponseSchema(BaseSchema):
    id: int
    created_at: datetime = Field(..., description="創建時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        return value.isoformat() if value else None
    
    @field_serializer('updated_at')
    def serialize_updated_at(self, value: Optional[datetime], _info) -> Optional[str]:
        return value.isoformat() if value else None
    
    model_config = ConfigDict(
        from_attributes=True
    )


class SlugSchema(BaseSchema):
    slug: str 