from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://caltrack_user:caltrack_password@db:5432/caltrack"
    food_planer_api_url: str = "http://foodplaner-backend:8000/api"  # For future integration
    
    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
