from uuid import UUID

from models.json_config import BaseOrjsonModel
from pydantic import BaseModel


class Genre(BaseModel):
    uuid: UUID
    name: str

    class Config(BaseOrjsonModel):
        pass