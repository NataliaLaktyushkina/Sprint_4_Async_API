import json
import pickle
from functools import lru_cache
from typing import List, Optional, Union

import requests
from aioredis import Redis
from core import config
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        pit_movies = requests.post(f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}/movies/_pit?keep_alive=1m')
        self.pit_id_movies = json.loads(pit_movies.content.decode('utf-8'))['id']

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_films_search(self, title: str, sort: str, genre_name: str,
                               page_number: Union[str, None],
                               page_size: Union[str, None]) -> List[Film]:
        key_string = str(title)+str(sort)+str(genre_name)+str(page_number)+str(page_size)
        films_search = await self._films_from_cache(key_string)
        if not films_search:
            if page_number and page_size:
                page_number = int(page_size) * (int(page_number) - 1) + 1
            films_search = await self._get_films_search_from_elastic(title, sort, genre_name, page_number,  page_size)
            if not films_search:
                return None
            await self._put_films_to_cache(key_string, films_search)

        return films_search

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _get_films_search_from_elastic(self, title, sort: str, genre_name: str,
                                             page_number: Union[int, None],
                                             page_size: Union[int, None]) -> List[Film]:
        if sort[0] == '-':
            direction = 'desc'
        else:
            direction = 'asc'
        try:
            body_query = {"query": {
                "bool": {
                    "must": []
                }
            }, "sort": [
                {"imdb_rating": {"order": direction}}
            ], "pit": {
                "id": self.pit_id_movies,
                "keep_alive": "2m"
            }}
            if title:
                body_query["query"]["bool"]["must"].append(
                    {"match": {"title": title}})
            if page_number and page_size:
                body_query["from"] = page_number
                body_query["size"] = page_size
            if genre_name:
                body_query["query"]["bool"]["must"].append(
                    {"match": {"genre": genre_name}})

            query_sorting = json.dumps(body_query)
            doc = await self.elastic.search(body=query_sorting)
        except NotFoundError:
            return None

        return [Film(**d['_source']) for d in doc['hits']['hits']]

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(str(film.id), film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _films_from_cache(self, key: str) -> List[Film]:

        data = await self.redis.get(key)
        if not data:
            return None

        unpacked_object = pickle.loads(data)

        return unpacked_object

    async def _put_films_to_cache(self, key: str, films: List[Film]):
        pickled_object = pickle.dumps(films)
        await self.redis.set(key, pickled_object, expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
