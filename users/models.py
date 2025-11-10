import datetime
import random
import mimetypes

import pytz
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.files.images import ImageFile
from django.db import models
from rest_framework import status
from rest_framework.exceptions import ValidationError

from users.enum import Gender, Provider
from users.constant import UserTokenConstrains, UserConstrains


def validate_avatar(avatar: ImageFile):
    if avatar.width != avatar.height:
        raise ValidationError('Avatar must have 1:1 ration', code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if avatar.size > UserConstrains.avatar_max_size:
        raise ValidationError(f'Avatar can not be larger than {UserConstrains.avatar_max_size} bytes', code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    mimetype = mimetypes.guess_type(avatar.name)[0]
    if not mimetype in UserConstrains.avatar_supported_types:
        raise ValidationError(f'Avatar type {mimetype} is not supported. Supported types are {",".join(UserConstrains.avatar_supported_types)}',
                              code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(
        max_length=20,
        null=True,
        choices=Gender.choices,
        default=None,
    )
    dob = models.DateField(null=True, default=None)
    avatar = models.ImageField(
        name='avatar',
        null=True,
        validators=[validate_avatar],
        upload_to="avatars",
    )
    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
        default=Provider.EMAIL,
    )

    class Meta(AbstractUser.Meta):
        db_table = "users"

    def set_password(self, password):
        validate_password(password=password)
        super().set_password(password)

class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    type = models.CharField(max_length=30)

    class Meta:
        db_table = "user_tokens"

    @classmethod
    def create(cls, user: User, token_type: str) -> "UserToken":
        created_at = datetime.datetime.now(tz=pytz.utc)

        token = cls(
            user=user,
            token=cls.__generate(UserTokenConstrains.get_length(token_type=token_type)),
            created_at=created_at,
            expires_at=UserTokenConstrains.get_expires_in(token_type=token_type, created_at=created_at),
            type=token_type,
        )

        token.save()

        return token

    @classmethod
    def __generate(cls, length: int) -> str:
        __characters = 'ABCDEFGHIJKLMNOPRSWY'
        __numbers = '0123456789'
        __special = '@!()'
        __pool = __characters + __numbers + __special + __characters.lower()

        token = ''
        for i in range(length):
            token += random.choice(__pool)

        return token
