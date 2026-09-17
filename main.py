from fastapi import FastAPI

from src.api import router as auth_router

app = FastAPI(
    title="Microservice for catalog and search for an online electronics store",
    description="микросервис каталога и поиска интернет магазина техники на FastAPI",
    version="1.0.0",
    debug=True
)

app.include_router(_router, prefix="/api/v1")
