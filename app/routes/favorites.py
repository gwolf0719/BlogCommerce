from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.favorite import Favorite
from app.schemas.product import ProductResponse
from pydantic import BaseModel

router = APIRouter(prefix="/favorites", tags=["收藏"])


class FavoriteRequest(BaseModel):
    """
    收藏商品請求 Schema
    
    用於添加商品到收藏清單的請求結構。
    """
    product_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1
            }
        }


class FavoriteResponse(BaseModel):
    """
    收藏項目響應 Schema
    
    包含完整的收藏項目資訊，包括商品詳細資料。
    """
    id: int
    product_id: int
    product: ProductResponse
    created_at: str
    
    class Config:
        from_attributes = True


@router.get(
    "/", 
    response_model=List[FavoriteResponse],
    summary="📖 獲取收藏清單",
    description="""
    ## 🎯 功能描述
    獲取當前用戶的收藏商品清單，包含完整的商品資訊。
    
    ## 📋 功能特點
    - 🔐 需要用戶認證
    - 📦 返回完整商品資訊
    - 🗂️ 按收藏時間排序
    - 🚀 即時數據獲取
    
    ## 📊 回應格式
    返回收藏商品陣列，每個項目包含：
    - 收藏記錄 ID
    - 商品完整資訊
    - 收藏時間
    """,
    responses={
        200: {
            "description": "成功獲取收藏清單",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "product_id": 123,
                            "product": {
                                "id": 123,
                                "name": "精選商品",
                                "price": "999.00",
                                "current_price": "799.00",
                                "is_on_sale": True,
                                "featured_image": "https://example.com/image.jpg",
                                "stock_quantity": 50,
                                "is_active": True
                            },
                            "created_at": "2024-01-15T10:30:00"
                        }
                    ]
                }
            }
        },
        401: {"description": "未認證用戶"}
    }
)
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    獲取用戶的收藏列表
    
    返回當前用戶的所有收藏商品，包含完整的商品資訊。
    """
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).all()
    
    # 格式化響應
    result = []
    for fav in favorites:
        result.append({
            "id": fav.id,
            "product_id": fav.product_id,
            "product": fav.product,
            "created_at": fav.created_at.isoformat()
        })
    
    return result


@router.post(
    "/",
    summary="⭐ 添加收藏",
    description="""
    ## 🎯 功能描述
    將指定商品添加到用戶的收藏清單中。
    
    ## 📋 功能特點
    - 🔐 需要用戶認證
    - ✅ 商品存在性驗證
    - 🚫 防止重複收藏
    - 📦 即時狀態更新
    
    ## 🔍 驗證規則
    - 商品必須存在且啟用
    - 不可重複收藏同一商品
    - 必須提供有效的商品 ID
    
    ## 📊 成功響應
    返回收藏成功訊息和收藏記錄 ID。
    """,
    responses={
        200: {
            "description": "收藏成功",
            "content": {
                "application/json": {
                    "example": {
                        "message": "收藏成功",
                        "favorite_id": 456
                    }
                }
            }
        },
        400: {"description": "商品已在收藏列表中"},
        401: {"description": "未認證用戶"},
        404: {"description": "商品不存在或已下架"}
    }
)
async def add_favorite(
    request: FavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加商品到收藏
    
    驗證商品存在性並防止重複收藏。
    """
    # 檢查商品是否存在
    product = db.query(Product).filter(
        Product.id == request.product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在或已下架"
        )
    
    # 檢查是否已收藏
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == request.product_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="該商品已在收藏列表中"
        )
    
    # 創建收藏記錄
    favorite = Favorite(
        user_id=current_user.id,
        product_id=request.product_id
    )
    
    db.add(favorite)
    db.commit()
    
    return {"message": "收藏成功", "favorite_id": favorite.id}


@router.delete(
    "/remove/{product_id}",
    summary="🗑️ 移除收藏",
    description="""
    ## 🎯 功能描述
    從用戶的收藏清單中移除指定商品。
    
    ## 📋 功能特點
    - 🔐 需要用戶認證
    - 🎯 精確商品定位
    - 🚫 防止無效操作
    - 📦 即時狀態更新
    
    ## 🔍 驗證規則
    - 收藏記錄必須存在
    - 只能移除自己的收藏
    - 提供有效的商品 ID
    
    ## 📊 成功響應
    返回移除成功確認訊息。
    """,
    responses={
        200: {
            "description": "移除收藏成功",
            "content": {
                "application/json": {
                    "example": {
                        "message": "已取消收藏"
                    }
                }
            }
        },
        401: {"description": "未認證用戶"},
        404: {"description": "收藏記錄不存在"}
    }
)
async def remove_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    從收藏中移除商品
    
    檢查收藏記錄存在性後進行移除操作。
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == product_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏記錄不存在"
        )
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "已取消收藏"}


@router.get(
    "/check/{product_id}",
    summary="🔍 檢查收藏狀態",
    description="""
    ## 🎯 功能描述
    檢查指定商品是否已被當前用戶收藏。
    
    ## 📋 功能特點
    - 🔐 需要用戶認證
    - ⚡ 快速狀態查詢
    - 🎯 精確商品定位
    - 📊 布林值回應
    
    ## 🔍 查詢邏輯
    - 查詢當前用戶的收藏記錄
    - 檢查指定商品是否存在
    - 返回收藏狀態布林值
    
    ## 📊 回應格式
    返回 JSON 物件，包含 is_favorited 布林值。
    """,
    responses={
        200: {
            "description": "成功檢查收藏狀態",
            "content": {
                "application/json": {
                    "example": {
                        "is_favorited": True
                    }
                }
            }
        },
        401: {"description": "未認證用戶"}
    }
)
async def check_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    檢查商品是否已收藏
    
    快速查詢用戶對特定商品的收藏狀態。
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == product_id
    ).first()
    
    return {"is_favorited": favorite is not None}


@router.get(
    "/count",
    summary="📊 獲取收藏數量",
    description="""
    ## 🎯 功能描述
    獲取當前用戶的收藏商品總數量。
    
    ## 📋 功能特點
    - 🔐 需要用戶認證
    - 📊 即時統計資料
    - ⚡ 快速數量查詢
    - 🎯 精確計數
    
    ## 🔍 統計邏輯
    - 統計用戶的收藏記錄總數
    - 排除已刪除的收藏
    - 實時更新數量
    
    ## 📊 回應格式
    返回 JSON 物件，包含 count 數量欄位。
    """,
    responses={
        200: {
            "description": "成功獲取收藏數量",
            "content": {
                "application/json": {
                    "example": {
                        "count": 15
                    }
                }
            }
        },
        401: {"description": "未認證用戶"}
    }
)
async def get_favorite_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    獲取用戶收藏數量
    
    統計當前用戶的收藏商品總數。
    """
    count = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).count()
    
    return {"count": count}