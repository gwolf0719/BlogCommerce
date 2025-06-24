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

router = APIRouter(prefix="/api/favorites", tags=["收藏"])


class FavoriteRequest(BaseModel):
    product_id: int


class FavoriteResponse(BaseModel):
    id: int
    product_id: int
    product: ProductResponse
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[FavoriteResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取用戶的收藏列表"""
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


@router.post("/")
async def add_favorite(
    request: FavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加商品到收藏"""
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


@router.delete("/remove/{product_id}")
async def remove_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """從收藏中移除商品"""
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


@router.get("/check/{product_id}")
async def check_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """檢查商品是否已收藏"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == product_id
    ).first()
    
    return {"is_favorited": favorite is not None}


@router.get("/count")
async def get_favorite_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取用戶收藏數量"""
    count = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).count()
    
    return {"count": count}