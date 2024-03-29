import asyncio
from dataclasses import dataclass
from typing import Optional

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch

from settings import get_test_settings

SERVICE_URL = 'http://127.0.0.1:80'
URL_REDIS = 'http://127.0.0.1:6379'

settings = get_test_settings()


@dataclass
class HTTPResponse:
    body: dict
    headers: [str]
    status: int


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'])
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client():
    client = await aioredis.create_redis_pool((settings.REDIS_HOST, settings.REDIS_PORT), minsize=10, maxsize=20)
    yield client
    client.close()
    await client.wait_closed()

@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = SERVICE_URL + '/api/v1' + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture
def make_get_request_redis(session):
    async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = 'redis-cli'
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


