import pytest
from testdata.test_data_genres import genre_id_to_try

@pytest.mark.parametrize('genre_id, expected', genre_id_to_try)
@pytest.mark.asyncio
async def test_genre(make_get_request, genre_id, expected):
    path = '/'.join(("/genres", genre_id))
    response = await make_get_request(path)

    assert response.status == 200
    assert response.body == expected
