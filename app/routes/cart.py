from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.product import Product
from app.models.discount_code import PromoCode, PromoType
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/cart", tags=["購物車"])


class CartItem(BaseModel):
    product_id: int
    quantity: int


class PromoCodeRequest(BaseModel):
    promo_code: str = Field(..., description="推薦碼")


class CartItemResponse(BaseModel):
    product_id: int
    quantity: int
    product: ProductResponse
    subtotal: float


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    total: float
    applied_promo: Dict[str, Any] | None = None
    discount_amount: float = 0


@router.get("/", response_model=CartResponse)
@router.get("", response_model=CartResponse)  # 添加不帶尾隨斜線的路由別名
def get_cart(request: Request, db: Session = Depends(get_db)):
    """取得購物車內容"""
    cart = request.session.get("cart", {})
    
    items = []
    total_items = 0
    subtotal = 0
    
    for product_id_str, quantity in cart.items():
        product_id = int(product_id_str)
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if product and product.is_active:
            product_data = ProductResponse.from_orm(product)
            
            item_subtotal = float(product.current_price) * quantity
            
            items.append({
                "product_id": product_id,
                "quantity": quantity,
                "product": product_data,
                "subtotal": item_subtotal
            })
            
            total_items += quantity
            subtotal += item_subtotal
    
    # 取得套用的推薦碼資訊
    applied_promo = request.session.get("applied_promo")
    discount_amount = 0
    
    if applied_promo:
        discount_amount = applied_promo.get("discount_amount", 0)
    
    final_total = max(0, subtotal - discount_amount)
    
    return CartResponse(
        items=items,
        total_items=total_items,
        subtotal=subtotal,
        total=final_total,
        applied_promo=applied_promo,
        discount_amount=discount_amount
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


@router.post("/apply-promo")
def apply_promo_code(
    promo_request: PromoCodeRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """套用推薦碼"""
    # 檢查推薦碼是否存在且有效
    promo_code = db.query(PromoCode).filter(
        PromoCode.code == promo_request.promo_code.upper(),
        PromoCode.is_active == True
    ).first()
    
    if not promo_code:
        raise HTTPException(status_code=400, detail="推薦碼不存在或已停用")
    
    # 檢查是否在有效期間內
    now = datetime.now()
    if promo_code.end_date and promo_code.end_date < now:
        raise HTTPException(status_code=400, detail="推薦碼已過期")
    
    # 檢查使用次數限制
    if promo_code.usage_limit and promo_code.used_count >= promo_code.usage_limit:
        raise HTTPException(status_code=400, detail="推薦碼已達使用次數上限")
    
    # 檢查最低消費金額
    cart = request.session.get("cart", {})
    subtotal = 0
    
    for product_id_str, quantity in cart.items():
        product_id = int(product_id_str)
        product = db.query(Product).filter(Product.id == product_id).first()
        if product and product.is_active:
            subtotal += float(product.current_price) * quantity
    
    if promo_code.min_order_amount and subtotal < float(promo_code.min_order_amount):
        raise HTTPException(
            status_code=400, 
            detail=f"購買金額需達到 NT${promo_code.min_order_amount} 才能使用此推薦碼"
        )
    
    # 計算推薦金額
    discount_amount = 0
    if promo_code.promo_type == PromoType.PERCENTAGE:
        discount_amount = subtotal * (float(promo_code.promo_value) / 100)
        # 將百分比推薦四捨五入到整數
        discount_amount = round(discount_amount)
    elif promo_code.promo_type == PromoType.AMOUNT:
        discount_amount = float(promo_code.promo_value)
    elif promo_code.promo_type == PromoType.FREE_SHIPPING:
        discount_amount = 0  # 免運費推薦待實現
    
    # 確保推薦金額不超過購物車總額
    discount_amount = min(discount_amount, subtotal)
    
    # 儲存推薦碼到 session
    request.session["applied_promo"] = {
        "id": promo_code.id,
        "code": promo_code.code,
        "name": promo_code.name,
        "promo_type": promo_code.promo_type.value,
        "promo_value": float(promo_code.promo_value),
        "discount_amount": discount_amount
    }
    
    return {
        "message": "推薦碼套用成功",
        "promo_code": {
            "id": promo_code.id,
            "code": promo_code.code,
            "name": promo_code.name,
            "promo_type": promo_code.promo_type.value,
            "promo_value": float(promo_code.promo_value)
        },
        "discount_amount": discount_amount
    }


@router.delete("/remove-promo")
def remove_promo_code(request: Request):
    """移除推薦碼"""
    if "applied_promo" in request.session:
        del request.session["applied_promo"]
    
    return {"message": "推薦碼已移除"} 