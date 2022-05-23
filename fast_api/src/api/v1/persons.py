from http import HTTPStatus
from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from services.persons import PersonService, get_person_service

from .films import FilmSorted

router = APIRouter()


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


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    films_and_roles = await person_service.get_films_and_roles(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return Person(uuid=person.id,
                  full_name=person.full_name,
                  films=films_and_roles
                  )


@router.get('/{person_id}/film', response_model=List[FilmSorted])
async def person_film_details(person_id: str,
                              person_service: PersonService = Depends(get_person_service)) -> List[FilmSorted]:
    films_list = await person_service.get_films(person_id)
    if not films_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')

    return [FilmSorted(uuid=fl.id,
                       title=fl.title,
                       imdb_rating=fl.imdb_rating) for fl in films_list]


@router.get('/', response_model=List[Person])
async def persons_search(query: str = Query(default=None),
                         page_number: Union[str, None] = Query(default=0, alias="page[number]"),
                         page_size: Union[str, None] = Query(default=0, alias="page[size]"),
                         person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons_search = await person_service.get_persons_search(query, page_number, page_size)
    if not persons_search:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    persons = []
    for person in persons_search:
        films_and_roles = await person_service.get_films_and_roles(person.id)
        persons.append(Person(uuid=person.id,
                              full_name=person.full_name,
                              films=films_and_roles
                              ))

    return persons
