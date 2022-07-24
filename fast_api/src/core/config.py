import os
# from logging import config as logging_config

# from core.logger import logger
from pydantic import BaseSettings
from dotenv import load_dotenv

IS_DOCKER = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)

if not IS_DOCKER:
    load_dotenv()   # take environment variables from .env.


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'movies')
    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    REDIS_PORT: str = os.getenv('REDIS_PORT')

    ELASTIC_PORT: str = os.getenv('ELASTIC_PORT')

    # JWT SETTINGS
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class PromSettings(Settings):

    REDIS_HOST: str = os.getenv('REDIS_HOST')
    ELASTIC_HOST: str = os.getenv('ELASTIC_HOST')


class DevSettings(Settings):

    REDIS_HOST: str
    ELASTIC_HOST: str

    class Config:
        fields = {
            "REDIS_HOST": {
                'env': 'REDIS_HOST_DEBUG'
            },
            "ELASTIC_HOST": {
                'env': 'ELASTIC_HOST_DEBUG'
            }
        }


def get_settings():
    environment = os.getenv('ENVIRONMENT')
    if environment == 'prom':
        return get_prom_settings()
    else:
        return get_dev_settings()


def get_prom_settings():
    return PromSettings()


def get_dev_settings():
    return DevSettings()

# Применяем настройки логирования
# logging_config.dictConfig(logger)
