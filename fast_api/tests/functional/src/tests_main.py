import pytest

from Sprint_4_Async_API.fast_api.tests.functional.testdata.test_data_genres import genre_id_to_try, genres_all, \
    genres_cache


class TestGenre:

    @pytest.mark.parametrize('genre_id, expected', genre_id_to_try)
    @pytest.mark.asyncio
    async def test_genre(self, make_get_request, genre_id, expected):
        path = '/'.join(("/genres", genre_id))
        response = await make_get_request(path)

        assert response.status == 200
        assert response.body == expected

    @pytest.mark.parametrize('len_genres, expected', genres_all)
    @pytest.mark.asyncio
    async def test_genre_all(sellf, make_get_request, len_genres, expected):
        path = "/genres"
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
        path = '/'.join(("/genres", genre_id))
        response = await make_get_request(path)

        # Check cache
        key = 'genres:' + genre_id
        response = await redis_client.exists(key)
        assert response == 1
