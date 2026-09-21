from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    id: UUID
    title: str
    slug: str
    parent_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

# Схема для отдачи дерева
class CategoryTreeResponse(CategoryBase):
    children: List["CategoryTreeResponse"] = []

# Важно для Pydantic, чтобы он корректно обработал рекурсивную ссылку
CategoryTreeResponse.model_rebuild()
