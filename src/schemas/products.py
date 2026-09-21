from uuid import UUID
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

# Базовая схема товара
class ProductRead(BaseModel):
    id: UUID
    sku: str
    category_id: UUID
    title: str
    description: Optional[str]
    price: Decimal
    stock: int
    is_active: bool
    attributes: Dict[str, Any] # Валидация нашего JSONB

    model_config = ConfigDict(from_attributes=True)

# Схема ответа с пагинацией списка товаров
class PaginatedProductResponse(BaseModel):
    items: List[ProductRead]
    total: int
    limit: int
    offset: int

