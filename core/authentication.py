from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import NotFound, ValidationError

from users.repo import UserTokenRepository

class ApiAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token_header = request.headers.get('Authorization')
        if not access_token_header:
            return None

        parts = access_token_header.split(' ')
        if len(parts) != 2:
            access_token_string = parts[0]
        else:
            access_token_string = parts[1]

        try:
            token = UserTokenRepository(request=request).find_token_by_token_string(token_string=access_token_string)
        except (NotFound, ValidationError) as e:
            raise exceptions.AuthenticationFailed(detail=str(e))

        return (token.user, token)