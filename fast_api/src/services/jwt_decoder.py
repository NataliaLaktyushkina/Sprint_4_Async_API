import jwt
from http import HTTPStatus
from typing import Union
import sys, os
sys.path.append(os.path.dirname(__file__) + '/..')
from core.config import get_settings

settings = get_settings()


def jwt_decoder(token: str) -> Union[dict, int]:
    try:
        decode_token = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        return decode_token
    except jwt.ExpiredSignatureError:
        # Signature has expired
        return HTTPStatus.UNAUTHORIZED