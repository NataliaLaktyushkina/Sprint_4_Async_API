from http import HTTPStatus
from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from services.films import FilmService, get_film_service

router = APIRouter()


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


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    # Перекладываем данные из models.Film в Film
    return Film(uuid=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating,
                description=film.description,
                genre=film.genre,
                directors=film.director,
                actors=film.actors,
                writers=film.writers
                )


@router.get('/', response_model=List[FilmSorted])
async def films_search(sort: str,
                       query: str = Query(default=None),
                       filter_genre: str = Query(default=None, alias="filter[genre]"),
                       page_number: Union[str, None] = Query(default=0, alias="page[number]"),
                       page_size: Union[str, None] = Query(default=0, alias="page[size]"),
                       film_service: FilmService = Depends(get_film_service)) -> List[FilmSorted]:

    films_sorted = await film_service.get_films_search(query, sort, filter_genre, page_number, page_size)
    if not films_sorted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')

    return [FilmSorted(uuid=fs.id,
                       title=fs.title,
                       imdb_rating=fs.imdb_rating) for fs in films_sorted]
