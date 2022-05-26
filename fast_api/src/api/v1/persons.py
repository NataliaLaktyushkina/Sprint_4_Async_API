from http import HTTPStatus
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from services.persons import PersonService, get_person_service

from .response_models.films import FilmSorted
from .response_models.person import Person
from .films import error_msg as films_error_msg

router = APIRouter()

error_msg = 'person(s) not found'

@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    films_and_roles = await person_service.get_films_and_roles(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_msg)

    return Person(uuid=person.id,
                  full_name=person.full_name,
                  films=films_and_roles
                  )


@router.get('/{person_id}/film', response_model=List[FilmSorted])
async def person_film_details(person_id: str,
                              person_service: PersonService = Depends(get_person_service)) -> List[FilmSorted]:
    films_list = await person_service.get_films(person_id)
    if not films_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=films_error_msg)

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
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_msg)
    persons = []
    for person in persons_search:
        films_and_roles = await person_service.get_films_and_roles(person.id)
        persons.append(Person(uuid=person.id,
                              full_name=person.full_name,
                              films=films_and_roles
                              ))

    return persons
