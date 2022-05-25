class Roles(BaseModel):
    role: str
    film_id: UUID
    film_title: Optional[str]
    film_imdb_rating: Optional[float]


class RolesShort(BaseModel):
    role: str
    film_id: UUID


class Person(BaseModel):
    uuid: UUID
    full_name: str
    films: List[RolesShort]