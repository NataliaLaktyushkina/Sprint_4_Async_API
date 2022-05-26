from typing import Optional
from uuid import UUID

from .json_config import BaseOrjsonModel


class Roles(BaseOrjsonModel):
    role: str
    film_id: UUID
    film_title: Optional[str]
    film_imdb_rating: Optional[float]


class RolesShort(BaseOrjsonModel):
    role: str
    film_id: UUID


class Person(BaseOrjsonModel):
    id: UUID
    full_name: str
