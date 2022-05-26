from uuid import UUID

from models.json_config import BaseOrjsonModel

class Genre(BaseOrjsonModel):
    uuid: UUID
    name: str
