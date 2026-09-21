import asyncio
import random
from decimal import Decimal
from uuid import uuid4

from faker import Faker
from sqlalchemy import delete  # Импортируем функцию удаления

# Ваши импорты моделей и фабрики сессий
from src.core.db import async_session_maker
from src.models import Category, Product

fake = Faker()

# Заготовленные параметры для техники
TECH_ATTRIBUTES = {
    "Smartphones": {
        "ram": ["8GB", "12GB", "16GB"],
        "storage": ["128GB", "256GB", "512GB"],
        "os": ["iOS", "Android"],
        "color": ["Black", "Silver", "Space Gray", "Green"]
    },
    "Laptops": {
        "ram": ["16GB", "32GB", "64GB"],
        "cpu": ["Intel Core i7", "Intel Core i9", "Apple M3", "AMD Ryzen 7"],
        "storage": ["512GB", "1TB", "2TB"],
        "display": ["13.3\"", "14.2\"", "15.6\"", "16\""]
    }
}


async def seed_data():
    async with async_session_maker() as session:
        # --- ОЧИСТКА БАЗЫ ДАННЫХ ---
        print("Очистка старых данных...")

        # Сначала удаляем продукты (зависимая таблица)
        await session.execute(delete(Product))

        # Затем удаляем категории (главная таблица)
        await session.execute(delete(Category))

        # Применяем изменения очистки перед добавлением новых
        await session.flush()
        print("База данных успешно очищена.")

        # --- ЗАПОЛНЕНИЕ ДАННЫМИ ---
        print("Начало генерации данных...")

        # 1. Создаем корневую категорию
        root_cat = Category(id=uuid4(), title="Электроника", slug="elektronika", parent_id=None)
        session.add(root_cat)
        await session.flush()  # Получаем id

        # 2. Создаем подкатегории
        sub_categories = [
            Category(id=uuid4(), title="Смартфоны", slug="smartphones", parent_id=root_cat.id),
            Category(id=uuid4(), title="Ноутбуки", slug="laptops", parent_id=root_cat.id)
        ]
        session.add_all(sub_categories)
        await session.flush()

        # 3. Генерируем товары для каждой подкатегории
        for cat in sub_categories:
            attr_pool = TECH_ATTRIBUTES.get(cat.title == "Смартфоны" and "Smartphones" or "Laptops")

            # Генерируем по 25 товаров (исправлено количество в range)
            for _ in range(500):
                # Формируем случайные характеристики техники в JSON
                product_attrs = {key: random.choice(values) for key, values in attr_pool.items()}

                product = Product(
                    id=uuid4(),
                    sku=f"TECH-{random.randint(100000, 999999)}",
                    category_id=cat.id,
                    title=f"{cat.title[:-1] if cat.title.endswith('ы') else cat.title} {fake.company()} {fake.word().upper()}",
                    description=fake.text(max_nb_chars=300),
                    price=Decimal(random.randint(300, 2500) * 100),  # Цены от 30к до 250к
                    stock=random.randint(0, 50),
                    is_active=True,
                    attributes=product_attrs
                )
                session.add(product)

        await session.commit()
        print("База данных успешно заполнена тестовыми категориями и техникой!")


if __name__ == "__main__":
    asyncio.run(seed_data())
