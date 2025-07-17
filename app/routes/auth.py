from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, UserUpdate, 
    UserChangePassword, Token
)
from app.auth import (
    authenticate_user, create_access_token, get_current_active_user
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["認證"])

@router.post(
    "/register", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="會員註冊",
    description="""
    新用戶註冊功能。
    
    ## 功能特色
    - 📧 支援電子郵件驗證
    - 🔐 密碼加密保護
    - 🛡️ 用戶名唯一性檢查
    - ✅ 自動建立用戶帳號
    
    ## 驗證規則
    - 電子郵件格式必須正確且唯一
    - 用戶名至少 3 個字元，只能包含字母和數字
    - 密碼至少 6 個字元
    - 確認密碼必須與密碼相符
    
    ## 注意事項
    - 註冊成功後用戶預設為啟用狀態
    - 新用戶預設角色為一般用戶
    - 系統會自動檢查電子郵件和用戶名的唯一性
    """,
    responses={
        201: {
            "description": "用戶註冊成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "newuser",
                        "full_name": "新用戶",
                        "phone": "0900000000",
                        "address": "台北市信義區",
                        "is_active": True,
                        "is_verified": False,
                        "role": "user",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                }
            }
        },
        400: {"description": "註冊資料驗證失敗或電子郵件/用戶名已存在"}
    }
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 檢查 email 是否已存在
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=400,
            detail="此電子郵件已被註冊"
        )
    
    # 檢查使用者名稱是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=400,
            detail="此使用者名稱已被使用"
        )
    
    # 建立新使用者
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address
    )
    db_user.set_password(user.password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post(
    "/login", 
    response_model=Token,
    summary="會員登入",
    description="""
    用戶登入功能，支援用戶名或電子郵件登入。
    
    ## 功能特色
    - 🔐 支援用戶名或電子郵件登入
    - 🎫 JWT Token 認證
    - 🕒 靈活的令牌過期時間設定
    - 💾 記住登入狀態選項
    
    ## 令牌過期時間
    - 一般登入：24 小時
    - 記住登入：30 天
    
    ## 注意事項
    - 登入成功後會回傳 JWT Token
    - Token 需要在後續 API 請求中的 Authorization header 中提供
    - 格式：`Authorization: Bearer <token>`
    """,
    responses={
        200: {
            "description": "登入成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "user123",
                            "full_name": "使用者",
                            "is_active": True,
                            "is_verified": True,
                            "role": "user"
                        }
                    }
                }
            }
        },
        401: {"description": "帳號或密碼錯誤，或帳號已停用"}
    }
)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    print(f"[DEBUG] 登入請求 - 使用者名稱: {user_credentials.username}, 密碼: {user_credentials.password}")
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號已停用"
        )
    
    # 建立 access token - 根據 remember 設定過期時間
    if user_credentials.remember:
        # 記住登入狀態：30 天
        access_token_expires = timedelta(days=settings.remember_token_expire_days)
    else:
        # 一般登入：24 小時
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """取得目前使用者資訊"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新目前使用者資訊"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password")
def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改密碼"""
    # 驗證目前密碼
    if not current_user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=400,
            detail="目前密碼錯誤"
        )
    
    # 設定新密碼
    current_user.set_password(password_data.new_password)
    db.commit()
    
    return {"message": "密碼已成功更新"} 