import datetime

class UserTokenConstrains:
    type_access_token = 'auth_token'
    type_refresh_token = 'refresh_token'
    type_verify_token = 'verify_token'
    type_reset_password_token = 'reset_password_token'
    type_magic_link_token = 'magic_link_token'

    @staticmethod
    def get_length(token_type: str) -> int:
        if token_type in [UserTokenConstrains.type_access_token, UserTokenConstrains.type_refresh_token]:
            return 200
        if token_type in [
            UserTokenConstrains.type_verify_token,
            UserTokenConstrains.type_reset_password_token,
            UserTokenConstrains.type_magic_link_token
        ]:
            return 50

        raise TypeError('Invalid token type')

    @staticmethod
    def get_expires_in(token_type: str, created_at: datetime.datetime) -> datetime.datetime:
        if token_type == UserTokenConstrains.type_access_token:
            return created_at + datetime.timedelta(days=30)
        if token_type == UserTokenConstrains.type_refresh_token:
            return created_at + datetime.timedelta(days=60)
        if token_type == UserTokenConstrains.type_verify_token:
            return created_at + datetime.timedelta(minutes=30)
        if token_type == UserTokenConstrains.type_reset_password_token:
            return created_at + datetime.timedelta(minutes=60)
        if token_type == UserTokenConstrains.type_magic_link_token:
            return created_at + datetime.timedelta(minutes=30)

        raise TypeError('Invalid token type')

class UserConstrains:
    avatar_max_size = 10000000000
    avatar_supported_types = [
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/svg+xml'
    ]