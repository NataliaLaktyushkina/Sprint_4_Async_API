from typing import Optional
from uuid import UUID

from .json_config import BaseOrjsonModel


class Genre(BaseOrjsonModel):
    id: UUID
    name: str
    description: Optional[str]
