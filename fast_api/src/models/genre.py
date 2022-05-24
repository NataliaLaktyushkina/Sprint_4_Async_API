from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from json_config import BaseOrjsonModel


class Genre(BaseModel, BaseOrjsonModel):
    id: UUID
    name: str
    description: Optional[str]
