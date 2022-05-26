from typing import List, Optional
from uuid import UUID

from models.json_config import BaseOrjsonModel


class Roles(BaseOrjsonModel):
    role: str
    film_id: UUID
    film_title: Optional[str]
    film_imdb_rating: Optional[float]


class RolesShort(BaseOrjsonModel):
    role: str
    film_id: UUID


class Person(BaseOrjsonModel):
    uuid: UUID
    full_name: str
    films: List[RolesShort]