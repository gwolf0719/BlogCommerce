from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User, pwd_context
from app.schemas.user import TokenData

# JWT 設定
security = HTTPBearer()


def get_password_hash(password: str) -> str:
    """加密密碼"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """建立 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """驗證 JWT Token"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證身份",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    return token_data


def get_current_user(
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """取得目前登入的使用者"""
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者不存在"
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """取得目前活躍的使用者"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="帳號已停用")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    """取得目前的管理員使用者"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足"
        )
    return current_user


def authenticate_user(db: Session, username: str, password: str):
    """驗證使用者帳號密碼"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user 