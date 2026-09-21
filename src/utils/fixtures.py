import asyncio
import random
from decimal import Decimal
from uuid import uuid4

from faker import Faker
from sqlalchemy import delete

# Ваши импорты моделей и фабрики сессий
from src.core.db import async_session_maker
from src.models import Category, Product

fake = Faker("ru_RU")

POSSIBLE_ATTRIBUTES = {
    "Цвет": ["Черный", "Белый", "Серебристый", "Графит", "Синий"],
    "Материал": ["Пластик", "Металл", "Стекло", "Алюминий"],
    "Гарантия": ["12 месяцев", "24 месяца", "36 месяцев"],
    "Страна-производитель": ["Китай", "Вьетнам", "Малайзия", "Германия"],
    "Класс энергопотребления": ["A+++", "A++", "A", "B"],
    "Мощность": ["500W", "1000W", "1500W", "2000W"],
    "Вес": ["1.2 кг", "2.5 кг", "5 кг", "10 кг"],
    "Размер": ["S", "M", "L", "XL", "Компактный", "Стандартный"]
}

BASE_CATEGORIES = [
    "Электроника", "Бытовая техника", "Дом и сад",
    "Автотовары", "Спорт и отдых", "Красота и здоровье",
    "Детские товары", "Книги и хобби", "Одежда и обувь"
]


# Вспомогательная функция для генерации безопасного уникального слага
def generate_safe_slug(prefix: str) -> str:
    # Просто берем случайное слово из списка и добавляем к нему UUID
    words = ['shop', 'store', 'market', 'hub', 'zone', 'tech', 'home', 'goods', 'item']
    return f"{prefix}-{random.choice(words)}-{str(uuid4())[:8]}"



async def seed_data():
    async with async_session_maker() as session:
        print("Очистка старых данных...")
        await session.execute(delete(Product))
        await session.execute(delete(Category))
        await session.flush()
        print("База данных успешно очищена.")

        print("Начало автоматической генерации каталога...")

        generated_skus = set()
        total_products = 0

        NUM_ROOT_CATEGORIES = 3
        NUM_SUB_CATEGORIES = 3
        NUM_PRODUCTS_PER_CAT = 500

        root_titles = random.sample(BASE_CATEGORIES, min(NUM_ROOT_CATEGORIES, len(BASE_CATEGORIES)))

        for r_idx, root_title in enumerate(root_titles):
            # Генерируем безопасный слаг латиницей (например: cat-shop-a1b2)
            root_slug = generate_safe_slug("cat")

            root_cat = Category(
                id=uuid4(),
                title=root_title,
                slug=root_slug,
                parent_id=None
            )
            session.add(root_cat)
            await session.flush()

            for s_idx in range(NUM_SUB_CATEGORIES):
                sub_title = f"Подкатегория {fake.word().capitalize()} {r_idx}-{s_idx}"
                # Генерируем безопасный слаг для подкатегории
                sub_slug = generate_safe_slug("sub")

                sub_cat = Category(
                    id=uuid4(),
                    title=sub_title,
                    slug=sub_slug,
                    parent_id=root_cat.id
                )
                session.add(sub_cat)
                await session.flush()

                num_attrs = random.randint(3, 5)
                chosen_attr_keys = random.sample(list(POSSIBLE_ATTRIBUTES.keys()), num_attrs)

                products_to_add = []

                for _ in range(NUM_PRODUCTS_PER_CAT):
                    while True:
                        short_uuid = str(uuid4())[:8].upper()
                        sku = f"AUTO-{short_uuid}"
                        if sku not in generated_skus:
                            generated_skus.add(sku)
                            break

                    product_attrs = {}
                    for key in chosen_attr_keys:
                        product_attrs[key] = random.choice(POSSIBLE_ATTRIBUTES[key])

                    title = f"Товар {fake.company()} {fake.word().upper()} {random.randint(100, 999)}"

                    product = Product(
                        id=uuid4(),
                        sku=sku,
                        category_id=sub_cat.id,
                        title=title,
                        description=fake.text(max_nb_chars=250),
                        price=Decimal(random.randint(50, 5000) * 100),
                        stock=random.randint(0, 100),
                        is_active=True,
                        attributes=product_attrs
                    )
                    products_to_add.append(product)

                session.add_all(products_to_add)
                await session.flush()

                total_products += len(products_to_add)
                print(f"  └─ Создано {NUM_PRODUCTS_PER_CAT} товаров для '{sub_title}'")

            print(f"Завершен корневой раздел: '{root_title}'")

        await session.commit()

        expected_total = NUM_ROOT_CATEGORIES * NUM_SUB_CATEGORIES * NUM_PRODUCTS_PER_CAT
        print(f"\n[УСПЕХ] База полностью нагенерирована автоматически!")
        print(f"Всего создано товаров: {total_products} / {expected_total}")


if __name__ == "__main__":
    asyncio.run(seed_data())
