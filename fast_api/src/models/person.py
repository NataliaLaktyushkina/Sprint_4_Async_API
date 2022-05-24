from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from json_config import BaseOrjsonModel


class Roles(BaseModel, BaseOrjsonModel):
    role: str
    film_id: UUID
    film_title: Optional[str]
    film_imdb_rating: Optional[float]


class RolesShort(BaseModel, BaseOrjsonModel):
    role: str
    film_id: UUID


class Person(BaseModel, BaseOrjsonModel):
    id: UUID
    full_name: str
