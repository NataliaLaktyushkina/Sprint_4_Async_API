from typing import Optional
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class Roles(BaseModel):
    role: str
    film_id: UUID
    film_title: Optional[str]
    film_imdb_rating: Optional[float]


class RolesShort(BaseModel):
    role: str
    film_id: UUID


class Person(BaseModel):
    id: UUID
    full_name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
