import json
import pickle
from functools import lru_cache
from typing import List, Optional, Union

import requests
from aioredis import Redis
from core.config import get_settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import FilmShort
from models.person import Person, Roles, RolesShort

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
settings = get_settings()


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        pit_persons = requests.post(f'http://{settings.ELASTIC_HOST}'
                                    f':{settings.ELASTIC_PORT}/persons/_pit?keep_alive=1m')
        self.pit_id_persons = json.loads(pit_persons.content.decode('utf-8'))['id']

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        key_string = 'persons:' + person_id
        person = await self._person_from_cache(key_string)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_films(self, person_id: str) -> List[FilmShort]:
        key_redis = ':'.join(('persons', str(person_id), 'films_and_roles'))
        films_and_roles = await self._persons_from_cache(key_redis)
        if not films_and_roles:
            films_and_roles = await self._get_films_and_roles_from_elastic(person_id)
            if not films_and_roles:
                return None

            await self._put_persons_to_cache(key_redis, films_and_roles)

        return [FilmShort(id=role.film_id,
                          title=role.film_title,
                          imdb_rating=role.film_imdb_rating) for role in films_and_roles]

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get('persons', person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def get_films_and_roles(self, person_id: str) -> List[RolesShort]:
        key_redis = ':'.join(('persons', str(person_id), 'films_and_roles'))
        films_and_roles = await self._persons_from_cache(key_redis)
        if not films_and_roles:
            films_and_roles = await self._get_films_and_roles_from_elastic(person_id)
            if not films_and_roles:
                return []
            await self._put_persons_to_cache(key_redis, films_and_roles)

        return [RolesShort(role=role.role, film_id=role.film_id) for role in films_and_roles]

    async def _get_films_and_roles_from_elastic(self, person_id: str) -> List[Roles]:
        person = await self._get_person_from_elastic(person_id)

        person_as_director = await self._get_films_by_role_and_person("director", person.full_name)
        person_as_writer = await self._get_films_by_role_and_person("writers_names", person.full_name)
        person_as_actor = await self._get_films_by_role_and_person("actors_names", person.full_name)

        roles = []
        roles.extend(person_as_director)
        roles.extend(person_as_writer)
        roles.extend(person_as_actor)
        return roles

    async def _get_films_by_role_and_person(self, role_name: str, full_name: str) -> List[Roles]:
        try:
            body_query = {
                "query": {
                    "match_phrase": {
                        role_name: {
                            "query": full_name
                        }
                    }
                },
            }

            query_sorting = json.dumps(body_query)
            doc = await self.elastic.search(index="movies", body=query_sorting)

        except NotFoundError:
            return None

        if role_name == 'writers_names':
            role_name = 'writer'
        if role_name == 'actors_names':
            role_name = 'actor'

        return [Roles(role=role_name,
                      film_id=d["_source"]["id"],
                      film_title=d["_source"]["title"],
                      film_imdb_rating=d["_source"]["imdb_rating"], ) for d in doc['hits']['hits']]

    async def get_persons_search(self, full_name: str,
                                 page_number: Union[str, None],
                                 page_size: Union[str, None]) -> Optional[List[Person]]:
        key_redis = ':'.join(('persons', full_name, str(page_number), str(page_size)))
        persons = await self._persons_from_cache(key_redis)
        if not persons:
            if page_number and page_size:
                page_number = int(page_size) * (int(page_number) - 1)
            persons = await self._get_persons_search_from_elastic(full_name, page_number, page_size)
            if not persons:
                return None
            await self._put_persons_to_cache(key_redis, persons)

        return persons

    async def _get_persons_search_from_elastic(self, full_name,
                                               page_number: Union[int, None],
                                               page_size: Union[int, None]) -> List[Person]:
        fn = "*" + full_name + "*"
        try:
            body_query = {"query": {
                "bool": {
                    "must": []
                }
            }, "pit": {
                "id": self.pit_id_persons,
                "keep_alive": "2m"
            }}
            if full_name:
                body_query["query"]["bool"]["must"].append(
                    {"match": {"full_name": fn}})
            if page_number and page_size:
                body_query["from"] = page_number
                body_query["size"] = page_size

            query_sorting = json.dumps(body_query)
            doc = await self.elastic.search(body=query_sorting)
        except NotFoundError:
            return None

        return [Person(**d['_source']) for d in doc['hits']['hits']]

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set('persons:' + str(person.id), person.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _persons_from_cache(self, key: str) -> Union[List[Person], List[FilmShort]]:

        data = await self.redis.get(key)
        if not data:
            return None

        unpacked_object = pickle.loads(data)

        return unpacked_object

    async def _put_persons_to_cache(self, key: str, persons: Union[List[Person], List[FilmShort]]):
        pickled_object = pickle.dumps(persons)
        await self.redis.set(key, pickled_object, expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
