import pytest
from testdata.test_data_genres import genre_id_to_try, genres_all


class GenreTests:

    @pytest.mark.parametrize('genre_id, expected', genre_id_to_try)
    @pytest.mark.asyncio
    async def test_genre(self, make_get_request, genre_id, expected):
        path = '/'.join(("/genres", genre_id))
        response = await make_get_request(path)

        assert response.status == 200
        assert response.body == expected

    @pytest.mark.parametrize('len_genres, expected', genres_all)
    @pytest.mark.asyncio
    async def test_genre_all(self, make_get_request, len_genres, expected):
        path = "/genres"
        response = await make_get_request(path)

        assert response.status == 200
        assert len(response.body) == len_genres
        # check first 3 elements
        assert response.body[0:3] == expected
