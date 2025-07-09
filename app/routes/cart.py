from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.product import Product
from pydantic import BaseModel, Field
import json

router = APIRouter(
    prefix="/api/cart",
    tags=["購物車"],
    responses={
        400: {"description": "請求參數錯誤"},
        404: {"description": "商品不存在"},
        500: {"description": "伺服器內部錯誤"}
    }
)


class CartItem(BaseModel):
    product_id: int
    quantity: int


class CartItemResponse(BaseModel):
    product_id: int
    quantity: int
    product: Dict[str, Any]
    subtotal: float


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    total: float


@router.get("/", response_model=CartResponse)
def get_cart(request: Request, db: Session = Depends(get_db)):
    """取得購物車內容"""
    # 從 session 或 cookie 取得購物車資料
    cart_data = request.session.get("cart", {})
    
    items = []
    subtotal = 0
    total_items = 0
    
    for product_id_str, quantity in cart_data.items():
        product_id = int(product_id_str)
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if product and product.is_active:
            item_subtotal = float(product.current_price) * quantity
            subtotal += item_subtotal
            total_items += quantity
            
            items.append(CartItemResponse(
                product_id=product_id,
                quantity=quantity,
                product={
                    "id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "current_price": float(product.current_price),
                    "is_on_sale": product.is_on_sale,
                    "featured_image": product.featured_image,
                    "slug": product.slug,
                    "stock_quantity": product.stock_quantity
                },
                subtotal=item_subtotal
            ))
    
    return CartResponse(
        items=items,
        total_items=total_items,
        subtotal=subtotal,
        total=subtotal  # 可以在這裡加入運費計算
    )


@router.post("/add")
def add_to_cart(
    item: CartItem,
    request: Request,
    db: Session = Depends(get_db)
):
    """加入商品到購物車"""
    # 檢查商品是否存在且啟用
    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或已停售")
    
    if product.stock_quantity < item.quantity:
        raise HTTPException(status_code=400, detail="庫存不足")
    
    # 從 session 取得購物車
    cart = request.session.get("cart", {})
    product_id_str = str(item.product_id)
    
    # 更新數量
    if product_id_str in cart:
        new_quantity = cart[product_id_str] + item.quantity
        if new_quantity > product.stock_quantity:
            raise HTTPException(status_code=400, detail="數量超過庫存")
        cart[product_id_str] = new_quantity
    else:
        cart[product_id_str] = item.quantity
    
    # 儲存到 session
    request.session["cart"] = cart
    
    return {"message": "商品已加入購物車", "quantity": cart[product_id_str]}


@router.put("/update")
def update_cart_item(
    item: CartItem,
    request: Request,
    db: Session = Depends(get_db)
):
    """更新購物車商品數量"""
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="數量必須大於0")
    
    # 檢查商品是否存在
    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或已停售")
    
    if product.stock_quantity < item.quantity:
        raise HTTPException(status_code=400, detail="數量超過庫存")
    
    # 更新購物車
    cart = request.session.get("cart", {})
    product_id_str = str(item.product_id)
    
    if product_id_str not in cart:
        raise HTTPException(status_code=404, detail="商品不在購物車中")
    
    cart[product_id_str] = item.quantity
    request.session["cart"] = cart
    
    return {"message": "購物車已更新", "quantity": item.quantity}


@router.delete("/remove/{product_id}")
def remove_from_cart(product_id: int, request: Request):
    """從購物車移除商品"""
    cart = request.session.get("cart", {})
    product_id_str = str(product_id)
    
    if product_id_str not in cart:
        raise HTTPException(status_code=404, detail="商品不在購物車中")
    
    del cart[product_id_str]
    request.session["cart"] = cart
    
    return {"message": "商品已從購物車移除"}


@router.delete("/clear")
def clear_cart(request: Request):
    """清空購物車"""
    request.session["cart"] = {}
    return {"message": "購物車已清空"} 