from pydantic import BaseModel

class Genre(BaseModel):
    uuid: UUID
    name: str