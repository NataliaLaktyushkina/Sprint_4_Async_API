

class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: Optional[str]
    genre: List[str]
    directors: List[str]
    actors: List[dict]
    writers: List[dict]


class FilmSorted(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float