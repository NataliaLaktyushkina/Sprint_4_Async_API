import pickle
from functools import lru_cache
from typing import List
from typing import Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.genre import Genre

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        key_string = 'genres:' + genre_id
        genre = await self._genre_from_cache(key_string)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(key_string, genre)

        return genre

    async def get_list(self) -> List[Genre]:
        key_redis = 'genres:list'
        genres_list = await self._genres_from_cache(key_redis)
        if not genres_list:
            genres_list = await self._get_genres_list_from_elastic()
            if not genres_list:
                return None
            await self._put_genres_to_cache(key_redis, genres_list)

        return genres_list

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _get_genres_list_from_elastic(self) -> Optional[List[Genre]]:
        try:
            doc = await self.elastic.search\
                    (index='genres',
                     body={"query": {"match_all": {}}},
                     size=100
                     )
        except NotFoundError:
            return None
        return [Genre(**d['_source']) for d in doc['hits']['hits']]

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None

        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, key: str, genre: Genre):
        await self.redis.set(key, genre.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _genres_from_cache(self, key: str) -> List[Genre]:

        data = await self.redis.get(key)
        if not data:
            return None

        unpacked_object = pickle.loads(data)

        return unpacked_object

    async def _put_genres_to_cache(self, key: str, genres: List[Genre]):
        pickled_object = pickle.dumps(genres)
        await self.redis.set(key, pickled_object, expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
