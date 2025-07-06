from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from app.schemas.base import BaseSchema, BaseResponseSchema
from app.models.user import UserRole


class UserBase(BaseSchema):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    password: str
    confirm_password: str
    
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
    username: str
    password: str
    remember: Optional[bool] = False


class UserUpdate(BaseSchema):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserChangePassword(BaseSchema):
    current_password: str
    new_password: str
    confirm_password: str
    
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
    is_active: bool
    is_verified: bool
    role: UserRole


class Token(BaseSchema):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseSchema):
    username: Optional[str] = None 