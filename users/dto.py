import datetime

import pytz

from users.models import User, UserToken
from users.serializers import LoginResponseSerializer
from users.constant import UserTokenConstrains

class LoginResponseDto:
    def __init__(self, user: dict, access_token: str, expires_in: int, refresh_token: str):
        self.__user = user
        self.__access_token = access_token
        self.__expires_in = expires_in
        self.__refresh_token = refresh_token

    def to_dict(self):
        return {
            'user': self.__user,
            'access_token': self.__access_token,
            'expires_in': self.__expires_in,
            'refresh_token': self.__refresh_token,
        }

class LoginResponseFactory:
    @staticmethod
    def create(user: User)->LoginResponseDto:
        access_token: UserToken = UserToken.create(user, token_type=UserTokenConstrains.type_access_token)

        return LoginResponseDto(
            user=LoginResponseSerializer(user).data,
            access_token=access_token.token,
            expires_in=int(access_token.expires_at.timestamp() - datetime.datetime.now(tz=pytz.UTC).timestamp()),
            refresh_token=UserToken.create(user, token_type=UserTokenConstrains.type_refresh_token).token
        )




