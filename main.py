from fastapi import FastAPI

from src.api.categories import router as categories_router
from src.api.products import router as products_router
from src.api.payments import router as payments_router

app = FastAPI(
    title="Microservice for catalog and search for an online electronics store",
    description="микросервис каталога и поиска интернет магазина техники на FastAPI",
    version="1.0.0",
    debug=True
)

app.include_router(categories_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")

