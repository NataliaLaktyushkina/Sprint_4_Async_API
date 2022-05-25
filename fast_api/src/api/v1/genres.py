from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from services.genres import GenreService, get_genre_service
from .response_models.genre import Genre

router = APIRouter()


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(uuid=genre.id,
                 name=genre.name,
                 )


@router.get('/', response_model=List[Genre])
async def genres_list(genre_service: GenreService = Depends(get_genre_service)) -> List[Genre]:
    genres_list = await genre_service.get_list()
    if not genres_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='no genres')

    return [Genre(uuid=gl.id, name=gl.name) for gl in genres_list]
