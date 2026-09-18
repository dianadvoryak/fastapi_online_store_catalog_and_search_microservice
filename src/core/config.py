from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Настройки PostgreSQL
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"

    # Настройки Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Настройки RabbitMQ
    RABBIT_USER: str = "guest"
    RABBIT_PASSWORD: str = "guest"
    RABBIT_HOST: str = "localhost"
    RABBIT_PORT: int = 5672

    # Автоматическое чтение из .env файла, если он есть
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()