from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.categories import CategoryTreeResponse
from src.services.category_service import CategoryService

router = APIRouter(prefix="/api/v1/catalog", tags=["Catalog"])


@router.get("/categories", response_model=List[CategoryTreeResponse])
async def get_category_tree(db: AsyncSession = Depends(get_async_session)):
    # Контроллер просто делегирует задачу сервису
    service = CategoryService(db)
    return await service.get_tree()
