import datetime

import pytz
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException, NotFound
from rest_framework.request import Request

from core.exception import NotVerboseValidationError
from users.models import UserToken, User


class UserRepository:
    def __init__(self, request: Request | None = None):
        self.__request = request

    def activate(self, user: User) -> User:
        user.is_active = True
        user.save()

        return user

    def reset_password(self, user: User, data: dict) -> User:
        user.set_password(data['password'])
        user.save()

        return user

class UserTokenRepository:
    def __init__(self, request: Request | None = None):
        self.__request = request

    def find_token_by_token_string(self, token_string: str) -> UserToken:
        token = UserToken.objects.filter(token=token_string).first()
        if not token:
            raise NotFound('Token not found')

        if token.used:
            raise NotVerboseValidationError('Token already used')

        if token.expires_at < datetime.datetime.now(tz=pytz.utc):
            raise NotVerboseValidationError('Token expired')

        return token

    def make_as_used(self, token: UserToken) -> UserToken:
        token.used = True
        token.save()

        return token


