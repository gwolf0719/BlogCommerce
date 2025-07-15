from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field
from app.schemas.base import BaseSchema, BaseResponseSchema
from app.models.user import UserRole


class UserBase(BaseSchema):
    """
    用戶基礎 Schema 類別
    
    包含用戶資料的基本欄位，用於各種用戶相關的操作。
    """
    email: EmailStr = Field(..., description="用戶電子郵件地址")
    username: str = Field(..., description="用戶名稱（唯一）", min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, description="用戶全名", max_length=100)
    phone: Optional[str] = Field(None, description="用戶電話號碼", max_length=20)
    address: Optional[str] = Field(None, description="用戶地址", max_length=500)


class UserCreate(UserBase):
    """
    用戶註冊 Schema 類別
    
    用於用戶註冊的請求結構，包含密碼驗證和確認密碼邏輯。
    
    驗證規則：
    - 用戶名稱至少 3 個字元，只能包含字母和數字
    - 密碼至少 6 個字元
    - 確認密碼必須與密碼相符
    """
    password: str = Field(..., description="用戶密碼", min_length=6)
    confirm_password: str = Field(..., description="確認密碼")
    
    @validator('username')
    def username_validation(cls, v):
        if not v or len(v) < 3:
            raise ValueError('使用者名稱至少需要 3 個字元')
        if not v.isalnum():
            raise ValueError('使用者名稱只能包含字母和數字')
        return v.lower()
    
    @validator('password')
    def password_validation(cls, v):
        if len(v) < 6:
            raise ValueError('密碼至少需要 6 個字元')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('確認密碼不符')
        return v


class UserLogin(BaseSchema):
    """
    用戶登入 Schema 類別
    
    用於用戶登入的請求結構。
    """
    username: str = Field(..., description="用戶名稱或電子郵件地址")
    password: str = Field(..., description="用戶密碼")
    remember: Optional[bool] = Field(False, description="記住登入狀態")


class UserUpdate(BaseSchema):
    """
    用戶資料更新 Schema 類別
    
    用於更新用戶個人資料的請求結構，所有欄位都是可選的。
    """
    full_name: Optional[str] = Field(None, description="用戶全名", max_length=100)
    phone: Optional[str] = Field(None, description="用戶電話號碼", max_length=20)
    address: Optional[str] = Field(None, description="用戶地址", max_length=500)


class UserChangePassword(BaseSchema):
    """
    用戶密碼變更 Schema 類別
    
    用於用戶變更密碼的請求結構，包含舊密碼驗證和新密碼確認。
    """
    current_password: str = Field(..., description="當前密碼")
    new_password: str = Field(..., description="新密碼", min_length=6)
    confirm_password: str = Field(..., description="確認新密碼")
    
    @validator('new_password')
    def password_validation(cls, v):
        if len(v) < 6:
            raise ValueError('密碼至少需要 6 個字元')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('確認密碼不符')
        return v


class UserResponse(UserBase, BaseResponseSchema):
    """
    用戶資料回應 Schema 類別
    
    用於回應用戶資料的結構，包含用戶基本資訊和系統狀態。
    """
    is_active: bool = Field(..., description="用戶是否啟用")
    is_verified: bool = Field(..., description="用戶是否已驗證")
    role: UserRole = Field(..., description="用戶角色")


class Token(BaseSchema):
    """
    認證令牌 Schema 類別
    
    用於回應用戶登入後的認證令牌和用戶資訊。
    """
    access_token: str = Field(..., description="JWT 存取令牌")
    token_type: str = Field(..., description="令牌類型")
    user: UserResponse = Field(..., description="用戶資料")


class TokenData(BaseSchema):
    """
    令牌資料 Schema 類別
    
    用於解析 JWT 令牌中的用戶資訊。
    """
    username: Optional[str] = Field(None, description="用戶名稱")


class UserListResponse(BaseSchema):
    """使用者列表的分頁回應"""
    items: list[UserResponse]
    total: int 