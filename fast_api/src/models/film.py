from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .json_config import BaseOrjsonModel


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float
    description: Optional[str]
    genre: List[str]
    director: Optional[List[str]]
    actors: List[dict]
    writers: List[dict]

    class Config(BaseOrjsonModel):
        pass


class FilmShort(BaseModel):
    id: UUID
    title: str
    imdb_rating: float

    class Config(BaseOrjsonModel):
        pass
