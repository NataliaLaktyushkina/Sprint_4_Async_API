from typing import List, Optional
from uuid import UUID

from models.json_config import BaseOrjsonModel

class Film(BaseOrjsonModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: List[str]
    directors: List[str]
    actors: List[dict]
    writers: List[dict]


class FilmSorted(BaseOrjsonModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float]


class FilmBySubscription(BaseOrjsonModel):
    by_subscription: bool