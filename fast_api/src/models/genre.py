from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .json_config import BaseOrjsonModel


class Genre(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config(BaseOrjsonModel):
        pass

