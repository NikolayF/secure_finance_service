from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    COOKIE_NAME: Optional[str] = None
    RABBITMQ_USER: Optional[str] = None
    RABBITMQ_PASS: Optional[str] = None
    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_PORT: Optional[str] = None
    RABBITMQ_QUEUE: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    @property
    def DATABASE_URL_asyncpg(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    @property
    def DATABASE_URL_psycopg(self):
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    model_config = SettingsConfigDict(env_file='.env')

@lru_cache()
def get_settings() -> Settings:
    return Settings()