from typing import List, Optional
from uuid import UUID

from models.json_config import BaseOrjsonModel
from pydantic import BaseModel


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
    uuid: UUID
    full_name: str
    films: List[RolesShort]

    class Config(BaseOrjsonModel):
        pass