from uuid import UUID, uuid4
from typing import Optional, List
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    # URL-префикс для фронтенда (например, "smartphones", "refrigerators")
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Ссылка на родительскую категорию (Self-referential)
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Отношения SQLAlchemy для удобной работы в коде
    # Получить родителя: category.parent
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")

    # Получить прямых потомков (подкатегории): category.children
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent")

    # Связь с товарами (одна категория содержит много товаров)
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")
