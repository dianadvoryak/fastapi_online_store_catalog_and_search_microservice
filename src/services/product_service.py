from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.product import Product

router = APIRouter(prefix="/api/v1/catalog", tags=["Catalog"])


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_filtered_products(
            self,
            category_id: UUID | None,
            price_min: float | None,
            price_max: float | None,
            limit: int,
            offset: int
    ) -> tuple[list[Product], int]:

        # 1. Строим базовый запрос списка товаров
        query = select(Product).where(Product.is_active == True)

        # Строим параллельный запрос для подсчета total count (без лимитов и оффсетов)
        count_query = select(func.count()).select_from(Product).where(Product.is_active == True)

        # 2. Применяем фильтры динамически
        if category_id:
            query = query.where(Product.category_id == category_id)
            count_query = count_query.where(Product.category_id == category_id)

        if price_min is not None:
            query = query.where(Product.price >= price_min)
            count_query = count_query.where(Product.price >= price_min)

        if price_max is not None:
            query = query.where(Product.price <= price_max)
            count_query = count_query.where(Product.price <= price_max)

        # 3. Применяем пагинацию и сортировку (сначала новые)
        query = query.order_by(Product.created_at.desc()).offset(offset).limit(limit)

        # 4. Выполняем запросы
        result_items = await self.db.execute(query)
        result_count = await self.db.execute(count_query)

        products = result_items.scalars().all()
        total_count = result_count.scalar() or 0

        return products, total_count

