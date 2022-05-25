from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .json_config import BaseOrjsonModel


class Roles(BaseModel):
    role: str
    film_id: UUID
    film_title: Optional[str]
    film_imdb_rating: Optional[float]

    class Config(BaseOrjsonModel):
        pass


class RolesShort(BaseModel):
    role: str
    film_id: UUID

    class Config(BaseOrjsonModel):
        pass


class Person(BaseModel):
    id: UUID
    full_name: str

    class Config(BaseOrjsonModel):
        pass
