from fastapi import FastAPI

from src.api import router as auth_router

app = FastAPI(
    title="online store catalog and search microservice",
    description="микросевис каталога и поиска интернет магазина на FastAPI",
    version="1.0.0",
    debug=True
)

app.include_router(_router, prefix="/api/v1")
