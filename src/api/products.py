from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.products import PaginatedProductResponse
from src.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/catalog", tags=["Catalog"])


@router.get("/products", response_model=PaginatedProductResponse)
async def get_products(
        category_id: UUID | None = Query(None, description="Фильтр по ID категории"),
        price_min: float | None = Query(None, description="Минимальная цена"),
        price_max: float | None = Query(None, description="Максимальная цена"),
        limit: int = Query(20, ge=1, le=100, description="Количество товаров на страницу"),
        offset: int = Query(0, ge=0, description="Смещение (пропущенные элементы)"),
        db: AsyncSession = Depends(get_async_session)
):
    """
    Получить список товаров интернет-магазина техники с пагинацией и базовой фильтрацией.
    """


    service = ProductService(db)
    # return await service.get_products()

    products, total = await service.get_filtered_products(
        category_id=category_id,
        price_min=price_min,
        price_max=price_max,
        limit=limit,
        offset=offset
    )

    return {
        "items": products,
        "total": total,
        "limit": limit,
        "offset": offset
    }


