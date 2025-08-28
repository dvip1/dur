import os
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

class Settings(BaseSettings):
    DATABASE_URL: str 
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config: 
        env_file=".env"
        env_file_encoding ="utf-8"

settings = Settings()
