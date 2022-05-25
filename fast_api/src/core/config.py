import os
from functools import lru_cache
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'movies')
    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    REDIS_HOST: str = os.getenv('REDIS_HOST')
    REDIS_PORT: str = os.getenv('REDIS_PORT')

    ELASTIC_HOST: str = os.getenv('ELASTIC_HOST')
    ELASTIC_PORT: str = os.getenv('ELASTIC_PORT')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


# @lru_cache()
def get_settings():
    return Settings()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
