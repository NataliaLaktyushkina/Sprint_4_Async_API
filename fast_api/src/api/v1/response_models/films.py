from typing import List, Optional
from uuid import UUID

from models.json_config import BaseOrjsonModel
from pydantic import BaseModel


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: Optional[str]
    genre: List[str]
    directors: List[str]
    actors: List[dict]
    writers: List[dict]

    class Config(BaseOrjsonModel):
        pass


class FilmSorted(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float

    class Config(BaseOrjsonModel):
        pass