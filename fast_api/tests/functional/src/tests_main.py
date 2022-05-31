import pytest

from testdata.test_data_films import film_ids_for_test, films_all, films_cache, film_keys
from testdata.test_data_genres import genre_ids_for_test, genres_all, genres_cache


def check_keys(response_dict, keys):
    for key in keys:
        if key not in response_dict:
            return False
    return True


class TestGenre:

    @pytest.mark.parametrize('genre_id, expected', genre_ids_for_test)
    @pytest.mark.asyncio
    async def test_genre(self, make_get_request, genre_id, expected):
        path = '/'.join(('/genres', genre_id))
        response = await make_get_request(path)

        assert response.status == 200
        assert response.body == expected

    @pytest.mark.parametrize('len_genres, expected', genres_all)
    @pytest.mark.asyncio
    async def test_genre_all(self, make_get_request, len_genres, expected):
        path = '/genres'
        response = await make_get_request(path)

        assert response.status == 200
        assert len(response.body) == len_genres
        # check first 3 elements
        assert response.body[0:3] == expected

    @pytest.mark.parametrize('genre_id', genres_cache)
    @pytest.mark.asyncio
    async def test_genre_cache(self, redis_client,
                               make_get_request, make_get_request_redis,
                               genre_id):
        # Clean cache
        redis_client.flushall()

        # make response
        path = '/'.join(('/genres', genre_id))
        await make_get_request(path)

        # Check cache
        key = 'genres:' + genre_id
        response = await redis_client.exists(key)
        assert response == 1


class TestFilm:

    @pytest.mark.parametrize('film_id, expected', film_ids_for_test)
    @pytest.mark.asyncio
    async def test_film(self, make_get_request, film_id, expected):
        path = '/'.join(('/films', film_id))
        response = await make_get_request(path)

        assert response.status == 200
        assert response.body == expected

    @pytest.mark.parametrize('keys', film_keys)
    @pytest.mark.parametrize('page_size, len_films', films_all)
    @pytest.mark.asyncio
    async def test_films_all(self, make_get_request,
                             page_size, len_films, keys):
        # Check first 10 films
        path = '/films'
        response = await make_get_request(path)

        assert response.status == 200
        assert len(response.body) == page_size
        assert check_keys(response.body[0], keys) is True

        # Check  amount of all films
        len_last_page = len_films % page_size
        last_page = len_films // page_size + 1
        path = '/films'
        params = {'page[number]': last_page, 'page[size]': page_size}
        response = await make_get_request(path, params)

        assert response.status == 200
        assert len(response.body) == len_last_page

    @pytest.mark.parametrize('film_id', films_cache)
    @pytest.mark.asyncio
    async def test_films_cache(self, redis_client,
                               make_get_request, make_get_request_redis,
                               film_id):
        # Clean cache
        redis_client.flushall()

        # make response
        path = '/'.join(('/films', film_id))
        await make_get_request(path)

        # Check cache
        key = 'movies:' + film_id
        response = await redis_client.exists(key)
        assert response == 1
