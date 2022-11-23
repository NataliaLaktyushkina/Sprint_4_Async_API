from typing import Optional
import aioredis
from aioredis import Redis

redis: Optional[Redis] = None

# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis