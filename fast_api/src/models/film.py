from typing import List, Optional
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float
    description: Optional[str]
    genre: List[str]
    director: Optional[List[str]]
    actors: List[dict]
    writers: List[dict]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FilmShort(BaseModel):
    id: UUID
    title: str
    imdb_rating: float

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
