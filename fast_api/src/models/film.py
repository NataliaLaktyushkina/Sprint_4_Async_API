from typing import List, Optional
from uuid import UUID

from .json_config import BaseOrjsonModel


class Film(BaseOrjsonModel):
    id: UUID
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: List[str]
    director: Optional[List[str]]
    actors: List[dict]
    writers: List[dict]


class FilmShort(BaseOrjsonModel):
    id: UUID
    title: str
    imdb_rating: Optional[float]

