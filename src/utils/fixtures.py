import asyncio
import random
from decimal import Decimal
from uuid import uuid4

from faker import Faker
from sqlalchemy import delete

# Ваши импорты моделей и фабрики сессий
from src.core.db import async_session_maker
from src.models import Category, Product

fake = Faker()

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
        print("Очистка старых данных...")
        await session.execute(delete(Product))
        await session.execute(delete(Category))
        await session.flush()
        print("База данных успешно очищена.")

        print("Начало генерации данных...")

        # 1. Создаем корневую категорию
        root_cat = Category(id=uuid4(), title="Электроника", slug="elektronika", parent_id=None)
        session.add(root_cat)
        await session.flush()

        # 2. Создаем подкатегории
        sub_categories = [
            Category(id=uuid4(), title="Смартфоны", slug="smartphones", parent_id=root_cat.id),
            Category(id=uuid4(), title="Ноутбуки", slug="laptops", parent_id=root_cat.id)
        ]
        session.add_all(sub_categories)
        await session.flush()

        # Набор для отслеживания уникальности SKU в рамках одной сессии генерации
        generated_skus = set()

        # 3. Генерируем товары для каждой подкатегории
        for cat in sub_categories:
            attr_pool = TECH_ATTRIBUTES.get(cat.title == "Смартфоны" and "Smartphones" or "Laptops")

            products_to_add = []

            for _ in range(500):  # Теперь генерируем честные 500 товаров на категорию
                # Генерируем УНИКАЛЬНЫЙ SKU
                while True:
                    # Из UUID берем первые 8 символов, это исключает дубли
                    short_uuid = str(uuid4())[:8].upper()
                    sku = f"TECH-{short_uuid}"
                    if sku not in generated_skus:
                        generated_skus.add(sku)
                        break

                product_attrs = {key: random.choice(values) for key, values in attr_pool.items()}

                # Добавляем случайное число к названию, чтобы названия тоже не дублировались
                title_prefix = cat.title[:-1] if cat.title.endswith('ы') else cat.title
                title = f"{title_prefix} {fake.company()} {fake.word().upper()} {random.randint(100, 999)}"

                product = Product(
                    id=uuid4(),
                    sku=sku,
                    category_id=cat.id,
                    title=title,
                    description=fake.text(max_nb_chars=300),
                    price=Decimal(random.randint(300, 2500) * 100),
                    stock=random.randint(0, 50),
                    is_active=True,
                    attributes=product_attrs
                )
                products_to_add.append(product)

            # Добавляем всю пачку из 500 товаров за раз (работает в разы быстрее)
            session.add_all(products_to_add)
            await session.flush()

        await session.commit()
        print("База данных успешно заполнена! Добавлено 1000 товаров.")


if __name__ == "__main__":
    asyncio.run(seed_data())
