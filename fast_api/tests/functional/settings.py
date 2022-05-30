from pydantic import BaseSettings, Field
from Sprint_4_Async_API.fast_api.src.core.config import Settings



class TestSettings(Settings):

    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: str = '6379'

    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: str = '9200'



def get_test_settings():
    return TestSettings()