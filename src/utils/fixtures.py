import asyncio
import random
from decimal import Decimal
from uuid import uuid4
from faker import Faker
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

# Ваши импорты моделей и фабрики сессий
from src.core.db import async_session_maker
from src.models import Category, Product

fake = Faker()

# Расширенная структура категорий и их уникальных атрибутов
CATALOG_STRUCTURE = {
    "Электроника": {
        "slug": "elektronika",
        "subcategories": {
            "Смартфоны": {
                "slug": "smartphones",
                "prefix": "Смартфон",
                "attributes": {
                    "ram": ["8GB", "12GB", "16GB"],
                    "storage": ["128GB", "256GB", "512GB"],
                    "os": ["iOS", "Android"],
                    "color": ["Black", "Silver", "Green"]
                }
            },
            "Ноутбуки": {
                "slug": "laptops",
                "prefix": "Ноутбук",
                "attributes": {
                    "ram": ["16GB", "32GB", "64GB"],
                    "cpu": ["Intel Core i7", "Apple M3", "AMD Ryzen 7"],
                    "storage": ["512GB", "1TB", "2TB"],
                    "display": ["14.2\"", "15.6\"", "16\""]
                }
            },
            "Умные часы": {
                "slug": "smartwatches",
                "prefix": "Умные часы",
                "attributes": {
                    "display_type": ["AMOLED", "OLED", "IPS"],
                    "size": ["41mm", "44mm", "45mm", "49mm"],
                    "has_cellular": ["Yes", "No"]
                }
            }
        }
    },
    "Бытовая техника": {
        "slug": "home-appliances",
        "subcategories": {
            "Холодильники": {
                "slug": "refrigerators",
                "prefix": "Холодильник",
                "attributes": {
                    "type": ["No Frost", "Direct Cool"],
                    "capacity": ["250L", "300L", "400L"],
                    "color": ["White", "Silver", "Black Graphite"]
                }
            },
            "Стиральные машины": {
                "slug": "washing-machines",
                "prefix": "Стиральная машина",
                "attributes": {
                    "max_load": ["6kg", "7kg", "8kg", "10kg"],
                    "inverter_motor": ["Yes", "No"],
                    "steam_function": ["Yes", "No"]
                }
            }
        }
    },
    "Аудио и видео": {
        "slug": "audio-video",
        "subcategories": {
            "Телевизоры": {
                "slug": "televisions",
                "prefix": "Телевизор",
                "attributes": {
                    "resolution": ["4K UHD", "Full HD", "8K OLED"],
                    "screen_size": ["43\"", "55\"", "65\"", "75\""],
                    "smart_tv": ["Android TV", "webOS", "Tizen"]
                }
            },
            "Наушники": {
                "slug": "headphones",
                "prefix": "Наушники",
                "attributes": {
                    "type": ["Wireless", "Wired"],
                    "form_factor": ["Over-Ear", "In-Ear"],
                    "anc": ["Yes", "No"]
                }
            }
        }
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

        generated_skus = set()
        total_products = 0

        # Обходим корневые категории (Электроника, Бытовая техника и т.д.)
        for root_title, root_data in CATALOG_STRUCTURE.items():
            root_cat = Category(
                id=uuid4(),
                title=root_title,
                slug=root_data["slug"],
                parent_id=None
            )
            session.add(root_cat)
            await session.flush()

            # Обходим подкатегории (Смартфоны, Ноутбуки и т.д.)
            for sub_title, sub_data in root_data["subcategories"].items():
                sub_cat = Category(
                    id=uuid4(),
                    title=sub_title,
                    slug=sub_data["slug"],
                    parent_id=root_cat.id
                )
                session.add(sub_cat)
                await session.flush()

                products_to_add = []
                attr_pool = sub_data["attributes"]
                prefix = sub_data["prefix"]

                # Генерируем по 500 товаров на каждую подкатегорию
                for _ in range(500):
                    # Гарантированно уникальный SKU
                    while True:
                        short_uuid = str(uuid4())[:8].upper()
                        sku = f"STORE-{short_uuid}"
                        if sku not in generated_skus:
                            generated_skus.add(sku)
                            break

                    # Случайный набор характеристик из пула
                    product_attrs = {key: random.choice(values) for key, values in attr_pool.items()}

                    # Генерация названия
                    title = f"{prefix} {fake.company()} {fake.word().upper()} {random.randint(100, 999)}"

                    product = Product(
                        id=uuid4(),
                        sku=sku,
                        category_id=sub_cat.id,
                        title=title,
                        description=fake.text(max_nb_chars=300),
                        price=Decimal(random.randint(150, 3000) * 100),  # Цены от 15к до 300к
                        stock=random.randint(0, 100),
                        is_active=True,
                        attributes=product_attrs
                    )
                    products_to_add.append(product)

                session.add_all(products_to_add)
                await session.flush()

                total_products += len(products_to_add)
                print(f"-> Добавлено 500 товаров в подкатегорию '{sub_title}'")

        await session.commit()
        print(
            f"\nУспех! База данных заполнена. Всего создано подкатегорий: {len(generated_skus) // 500}, товаров: {total_products}")


if __name__ == "__main__":
    asyncio.run(seed_data())
