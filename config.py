from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Sales"
    DEBUG_MODE: bool = False
    CORS_ORIGINS: str = "http://localhost:5173"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "salesdb"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_URL: str = ""

    class Config:
        env_file = ".env"

settings = Settings()

settings.DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
settings.CORS_ORIGINS = list(map(lambda s: s.strip(), settings.CORS_ORIGINS.split(",")))