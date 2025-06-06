from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from app.database import get_db
from app.models.tag import Tag
from app.models.post import Post, post_tags
from app.models.product import Product, product_tags

router = APIRouter(prefix="/api/tags", tags=["tags"])

@router.get("/")
async def get_all_tags(
    content_type: Optional[str] = Query(None, description="過濾內容類型: blog, product"),
    search: Optional[str] = Query(None, description="搜尋標籤名稱"),
    db: Session = Depends(get_db)
):
    """獲取所有標籤"""
    query = db.query(Tag)
    
    if content_type:
        if content_type == "blog":
            query = query.filter(Tag.type == "blog")
        elif content_type == "product":  
            query = query.filter(Tag.type == "product")
    
    if search:
        query = query.filter(Tag.name.contains(search))
    
    tags = query.order_by(Tag.name).all()
    
    # 計算每個標籤的使用次數，只返回有內容的標籤
    result = []
    for tag in tags:
        if tag.type == "blog":
            count = db.query(func.count(post_tags.c.post_id)).filter(
                post_tags.c.tag_id == tag.id
            ).scalar()
        else:
            count = db.query(func.count(product_tags.c.product_id)).filter(
                product_tags.c.tag_id == tag.id
            ).scalar()
        
        # 只返回有內容的標籤（count > 0）
        if count > 0:
            result.append({
                "id": tag.id,
                "name": tag.name,
                "slug": tag.slug,
                "description": tag.description,
                "type": tag.type,
                "count": count,
                "created_at": tag.created_at.isoformat()
            })
    
    return result

@router.get("/{tag_slug}")
async def get_tag_by_slug(tag_slug: str, db: Session = Depends(get_db)):
    """根據 slug 獲取標籤詳情"""
    tag = db.query(Tag).filter(Tag.slug == tag_slug).first()
    if not tag:
        raise HTTPException(status_code=404, detail="標籤不存在")
    
    # 計算使用次數
    if tag.type == "blog":
        count = db.query(func.count(post_tags.c.post_id)).filter(
            post_tags.c.tag_id == tag.id
        ).scalar()
    else:
        count = db.query(func.count(product_tags.c.product_id)).filter(
            product_tags.c.tag_id == tag.id
        ).scalar()
    
    return {
        "id": tag.id,
        "name": tag.name,
        "slug": tag.slug,
        "description": tag.description,
        "type": tag.type,
        "count": count,
        "created_at": tag.created_at.isoformat()
    }

@router.get("/{tag_slug}/posts")
async def get_posts_by_tag(
    tag_slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """獲取特定標籤的文章"""
    tag = db.query(Tag).filter(Tag.slug == tag_slug, Tag.type == "blog").first()
    if not tag:
        raise HTTPException(status_code=404, detail="標籤不存在")
    
    # 獲取該標籤的文章
    posts_query = db.query(Post).join(post_tags).filter(
        post_tags.c.tag_id == tag.id,
        Post.is_published == True
    ).order_by(Post.created_at.desc())
    
    total = posts_query.count()
    posts = posts_query.offset(skip).limit(limit).all()
    
    return {
        "tag": {
            "id": tag.id,
            "name": tag.name,
            "slug": tag.slug,
            "description": tag.description
        },
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "excerpt": post.excerpt,
                "featured_image": post.featured_image,
                "created_at": post.created_at.isoformat(),
                "reading_time": post.reading_time,
                "categories": [{"id": cat.id, "name": cat.name, "slug": cat.slug} for cat in post.categories],
                "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in post.tags]
            } for post in posts
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{tag_slug}/products") 
async def get_products_by_tag(
    tag_slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """獲取特定標籤的商品"""
    tag = db.query(Tag).filter(Tag.slug == tag_slug, Tag.type == "product").first()
    if not tag:
        raise HTTPException(status_code=404, detail="標籤不存在")
    
    # 獲取該標籤的商品
    products_query = db.query(Product).join(product_tags).filter(
        product_tags.c.tag_id == tag.id,
        Product.is_active == True
    ).order_by(Product.created_at.desc())
    
    total = products_query.count()
    products = products_query.offset(skip).limit(limit).all()
    
    return {
        "tag": {
            "id": tag.id,
            "name": tag.name,
            "slug": tag.slug,
            "description": tag.description
        },
        "products": [
            {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "short_description": product.short_description,
                "price": float(product.price),
                "sale_price": float(product.sale_price) if product.sale_price else None,
                "current_price": float(product.sale_price) if product.sale_price else float(product.price),
                "featured_image": product.featured_image,
                "is_featured": product.is_featured,
                "stock_quantity": product.stock_quantity,
                "created_at": product.created_at.isoformat(),
                "categories": [{"id": cat.id, "name": cat.name, "slug": cat.slug} for cat in product.categories],
                "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in product.tags]
            } for product in products
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    } 