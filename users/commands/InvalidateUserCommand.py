from django.core.management import BaseCommand

from users.constant import UserTokenConstrains
from users.models import UserToken, User

class InvalidateUserCommand(BaseCommand):
    help = 'Invalidate user by removing all of his access and refresh tokens'

    def add_arguments(self, parser):
        parser.add_argument('email', required=True, type=str)

    def handle(self, *args, **options):
        email = options['email']

        if not email:
            self.stderr.write('Email is required')

        user = User.objects.filter(email=email).first()
        if not user:
            self.stderr.write('User not found')

        deleted = UserToken.objects.filter(
            user=user,
            type__in = (UserTokenConstrains.type_verify_token, UserTokenConstrains.type_refresh_token)
        ).delete()

        if deleted[0] > 0:
            self.stdout.write('All tokens deleted. User is invalidated')
        else:
            self.stderr.write('Could not delete tokens. User was not invalidated')