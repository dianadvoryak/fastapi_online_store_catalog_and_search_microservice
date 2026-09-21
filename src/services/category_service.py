from typing import List, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.category import Category
from src.schemas.categories import CategoryTreeResponse


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tree(self) -> List[CategoryTreeResponse]:
        """Основной метод сервиса, который дергает роутер
            Получить полную иерархическую структуру (дерево) категорий.
            Выполняет всего 1 быстрый запрос к базе данных.
        """
        # Выбираем абсолютно все категории плоским списком
        result = await self.db.execute(select(Category))
        flat_categories = result.scalars().all()
        # Собираем в дерево на стороне приложения
        return self._build_category_tree(flat_categories)

    # def _build_category_tree(self, categories: List[Category]) -> List[CategoryTreeResponse]:
    #     """
    #         Алгоритм сборки дерева из плоского списка за один проход O(N).
    #         Внутренний (приватный) метод бизнес-логики для сборки дерева
    #     """
    #     # 1. Маппим все категории в Pydantic-схемы и сохраняем в словарь по ID
    #     nodes: Dict[UUID, CategoryTreeResponse] = {
    #         cat.id: CategoryTreeResponse.model_validate(cat) for cat in categories
    #     }
    #     tree: List[CategoryTreeResponse] = []
    #
    #     # 2. Распределяем дочерние категории по родителям
    #     for node in nodes.values():
    #         if node.parent_id is None:
    #             # Если родителя нет — это корневой элемент дерева
    #             tree.append(node)
    #         else:
    #             # Если родитель есть, находим его в словаре и добавляем в children
    #             parent_node = nodes.get(node.parent_id)
    #             if parent_node:
    #                 # Так как это объекты Pydantic, мы можем напрямую мутировать список
    #                 parent_node.children.append(node)
    #
    #     return tree


    def _build_category_tree(self, categories: List[Category]) -> List[CategoryTreeResponse]:
        # 1. Маппим данные БЕЗ автоматического обращения к cat.children
        nodes: Dict[UUID, CategoryTreeResponse] = {
            cat.id: CategoryTreeResponse(
                id=cat.id,
                title=cat.title,
                slug=cat.slug,
                parent_id=cat.parent_id,
                children=[]  # Инициализируем пустым списком вручную
            ) for cat in categories
        }

        tree: List[CategoryTreeResponse] = []

        # 2. Распределяем по родителям (ваш алгоритм остается без изменений)
        for node in nodes.values():
            if node.parent_id is None:
                tree.append(node)
            else:
                parent_node = nodes.get(node.parent_id)
                if parent_node:
                    parent_node.children.append(node)

        return tree
