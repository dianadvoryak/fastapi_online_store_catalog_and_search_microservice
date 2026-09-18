from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import String, Numeric, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Product(Base):
    __tablename__ = "products"

    # Основные идентификаторы и связи
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)  # Артикул
    category_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),  # RESTRICT не даст удалить категорию, пока в ней есть товары
        nullable=False,
        index=True
    )

    # Базовая информация о товаре
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(default=0)  # Остаток на складе
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    # Динамические характеристики (для техники: {"ram": 16, "cpu": "M3", "color": "space_gray"})
    attributes: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Системные поля
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Индексы для быстрого поиска и фильтрации по JSONB
    __table_args__ = (
        Index("ix_products_attributes_gin", "attributes", postgresql_using="gin"),
    )

    # Обратная связь: product.category
    category: Mapped["Category"] = relationship("Category", back_populates="products")

