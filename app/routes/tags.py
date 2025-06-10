from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from app.database import get_db
from app.models.tag import Tag, TagType
from app.models.post import Post, post_tags
from app.models.product import Product, product_tags

router = APIRouter(prefix="/api/tags", tags=["tags"])

@router.get("/")
async def get_all_tags(
    content_type: Optional[str] = Query(None, description="過濾內容類型: blog, product"),
    search: Optional[str] = Query(None, description="搜尋標籤名稱"),
    db: Session = Depends(get_db)
):
    """獲取所有標籤，合併相同 slug 的標籤"""
    query = db.query(Tag)
    
    if content_type:
        if content_type == "blog":
            query = query.filter(Tag.type == TagType.BLOG)
        elif content_type == "product":  
            query = query.filter(Tag.type == TagType.PRODUCT)
    
    if search:
        query = query.filter(Tag.name.contains(search))
    
    tags = query.order_by(Tag.name).all()
    
    # 按 slug 分組標籤，合併相同 slug 的標籤
    grouped_tags = {}
    for tag in tags:
        if tag.slug not in grouped_tags:
            grouped_tags[tag.slug] = []
        grouped_tags[tag.slug].append(tag)
    
    # 計算每個標籤組的使用次數，只返回有內容的標籤
    result = []
    for slug, tag_group in grouped_tags.items():
        total_count = 0
        primary_tag = tag_group[0]  # 取第一個作為主要標籤
        
        # 計算所有類型的使用次數
        for tag in tag_group:
            if tag.type == TagType.BLOG:
                count = db.query(func.count(post_tags.c.post_id)).filter(
                    post_tags.c.tag_id == tag.id
                ).scalar()
            else:
                count = db.query(func.count(product_tags.c.product_id)).filter(
                    product_tags.c.tag_id == tag.id
                ).scalar()
            total_count += count
        
        # 只返回有內容的標籤（total_count > 0）
        if total_count > 0:
            result.append({
                "id": primary_tag.id,
                "name": primary_tag.name,
                "slug": primary_tag.slug,
                "description": primary_tag.description,
                "type": "mixed" if len(tag_group) > 1 else primary_tag.type,
                "count": total_count,
                "created_at": primary_tag.created_at.isoformat()
            })
    
    # 按名稱排序
    result.sort(key=lambda x: x['name'])
    return result

@router.get("/{tag_slug}")
async def get_tag_by_slug(tag_slug: str, db: Session = Depends(get_db)):
    """根據 slug 獲取標籤詳情，合併所有類型的標籤"""
    # 查找所有匹配 slug 的標籤（可能有 blog 和 product 兩種類型）
    tags = db.query(Tag).filter(Tag.slug == tag_slug).all()
    if not tags:
        raise HTTPException(status_code=404, detail="標籤不存在")
    
    # 合併標籤資訊，優先取第一個標籤的名稱和描述
    primary_tag = tags[0]
    total_count = 0
    
    # 計算所有類型的使用次數
    for tag in tags:
        if tag.type == TagType.BLOG:
            count = db.query(func.count(post_tags.c.post_id)).filter(
                post_tags.c.tag_id == tag.id
            ).scalar()
        else:
            count = db.query(func.count(product_tags.c.product_id)).filter(
                product_tags.c.tag_id == tag.id
            ).scalar()
        total_count += count
    
    return {
        "id": primary_tag.id,
        "name": primary_tag.name,
        "slug": primary_tag.slug,
        "description": primary_tag.description,
        "type": "mixed",  # 表示混合類型
        "count": total_count,
        "created_at": primary_tag.created_at.isoformat()
    }

@router.get("/{tag_slug}/posts")
async def get_posts_by_tag(
    tag_slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """獲取特定標籤的文章"""
    # 查找所有匹配的 blog 類型標籤
    blog_tags = db.query(Tag).filter(Tag.slug == tag_slug, Tag.type == TagType.BLOG).all()
    if not blog_tags:
        # 如果沒有找到部落格標籤，返回空結果而不是錯誤
        return {
            "tag": {
                "name": tag_slug,
                "slug": tag_slug,
                "description": None
            },
            "posts": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }
    
    # 獲取所有匹配標籤的文章
    tag_ids = [tag.id for tag in blog_tags]
    posts_query = db.query(Post).join(post_tags).filter(
        post_tags.c.tag_id.in_(tag_ids),
        Post.is_published == True
    ).order_by(Post.created_at.desc())
    
    total = posts_query.count()
    posts = posts_query.offset(skip).limit(limit).all()
    
    primary_tag = blog_tags[0]
    return {
        "tag": {
            "id": primary_tag.id,
            "name": primary_tag.name,
            "slug": primary_tag.slug,
            "description": primary_tag.description
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
    # 查找所有匹配的 product 類型標籤
    product_tag_list = db.query(Tag).filter(Tag.slug == tag_slug, Tag.type == TagType.PRODUCT).all()
    if not product_tag_list:
        # 如果沒有找到商品標籤，返回空結果而不是錯誤
        return {
            "tag": {
                "name": tag_slug,
                "slug": tag_slug,
                "description": None
            },
            "products": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }
    
    # 獲取所有匹配標籤的商品
    tag_ids = [tag.id for tag in product_tag_list]
    products_query = db.query(Product).join(product_tags).filter(
        product_tags.c.tag_id.in_(tag_ids),
        Product.is_active == True
    ).order_by(Product.created_at.desc())
    
    total = products_query.count()
    products = products_query.offset(skip).limit(limit).all()
    
    primary_tag = product_tag_list[0]
    return {
        "tag": {
            "id": primary_tag.id,
            "name": primary_tag.name,
            "slug": primary_tag.slug,
            "description": primary_tag.description
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