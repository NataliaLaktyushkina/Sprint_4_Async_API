from http import HTTPStatus
from typing import List, Union


from fastapi import APIRouter, Depends, HTTPException, Query
from services.films import FilmService, get_film_service
from .response_models.films import Film, FilmSorted, FilmBySubscription
router = APIRouter()

error_msg = 'film(s) not found'


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_msg)

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
async def films_search(sort: str = Query(default='-'),
                       query: str = Query(default=None),
                       filter_genre: str = Query(default=None, alias="filter[genre]"),
                       page_number: Union[str, None] = Query(default=0, alias="page[number]"),
                       page_size: Union[str, None] = Query(default=0, alias="page[size]"),
                       film_service: FilmService = Depends(get_film_service)) -> List[FilmSorted]:

    films_sorted = await film_service.get_films_search(query, sort, filter_genre, page_number, page_size)
    if not films_sorted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_msg)

    return [FilmSorted(uuid=fs.id,
                       title=fs.title,
                       imdb_rating=fs.imdb_rating) for fs in films_sorted]


@router.get('/{film_id}/by_subscription', response_model=FilmBySubscription)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> FilmBySubscription:
    return  await film_service.by_subscription(film_id)