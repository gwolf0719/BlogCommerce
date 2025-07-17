import json
from typing import Optional, List, Type, Any
from decimal import Decimal
from pydantic import field_validator, GetCoreSchemaHandler
from pydantic_core import CoreSchema, PydanticCustomError, core_schema

from app.schemas.base import BaseSchema, BaseResponseSchema

class JsonList(List[str]):
    """
    自定義 Pydantic 類型，用於將列表序列化為 JSON 字串並反序列化。
    """
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def validate_from_json_string(value: str) -> List[str]:
            try:
                list_value = json.loads(value)
                if not isinstance(list_value, list):
                    raise PydanticCustomError(
                        'json_list_type', 'Input is not a valid JSON list'
                    )
                return [str(item) for item in list_value]
            except json.JSONDecodeError:
                raise PydanticCustomError(
                    'json_list_decode', 'Input is not a valid JSON string'
                )

        def serialize_to_json_string(value: List[str]) -> str:
            return json.dumps(value)

        s = core_schema.json_or_python_schema(
            json_schema=core_schema.no_info_after_validator_function(
                validate_from_json_string, core_schema.str_schema()
            ),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(list),
                core_schema.no_info_after_validator_function(
                    validate_from_json_string, core_schema.str_schema()
                )
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_to_json_string,
                info_arg=False,
                return_schema=core_schema.str_schema()
            )
        )
        return s

class ProductBase(BaseSchema):
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Decimal
    sale_price: Optional[Decimal] = None
    sku: Optional[str] = None
    stock_quantity: int = 0
    is_active: bool = True
    is_featured: bool = False
    featured_image: Optional[str] = None
    # gallery_images: Optional[JsonList] = [] # 移除相冊圖片功能
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    slug: Optional[str] = None

    # 移除 convert_gallery_images_to_json_string 驗證器

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None

class ProductResponse(ProductBase, BaseResponseSchema):
    id: int
    view_count: int = 0
    description_html: Optional[str] = None  # 新增 Markdown 渲染後的 HTML

    # 【核心修正點】: 為特色圖片加上路徑前綴
    @field_validator('featured_image', mode='before')
    @classmethod
    def add_featured_image_prefix(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith('/static/'):
            return f"/static/images/{v}"
        return v

    # 移除 add_gallery_image_prefix 驗證器，因為 JsonList 會處理

    class Config:
        from_attributes = True

class ProductListResponse(BaseSchema):
    items: List[ProductResponse]
    total: int
