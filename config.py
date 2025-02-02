from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Sales"
    DEBUG_MODE: bool = False
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "salesdb"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    class Config:
        env_file = ".env"

settings = Settings()