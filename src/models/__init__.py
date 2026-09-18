from src.models.base import Base
from src.models.product import Product
from src.models.category import Category

# Экспортируем все для Alembic
__all__ = ["Base", "Product", "Category"]
