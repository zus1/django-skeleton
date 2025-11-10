import os

from django.template.loader import render_to_string
from users.constant import UserTokenConstrains
from users.models import User, UserToken
from django.conf import settings
from core.mailer import Mailer

class UserEmail(Mailer):
    def __init__(self, user: User):
        self.__user = user
        self.__from = settings.EMAIL_FROM_ADDRESS
        self.__frontend_url = settings.FRONTEND_URL

        super().__init__()

    def send_email_verification(self):
        full_name = self.__user.get_full_name()
        token = UserToken.create(user=self.__user, token_type=UserTokenConstrains.type_verify_token)
        url = self.__frontend_url + settings.REDIRECT_PATH_VERIFY + '?token=' + token.token

        message = f'''
        Hello {full_name}
        Please click on link below to verify your email address
        {url}
        This is an automatically generated message. Please do not reply to this email.
        '''

        html = render_to_string('verify.html', {
            'full_name': full_name,
            'url': url
        })

        return self.send(subject='Verify email', to=self.__user.email, html=html, text=message, reply=False)

    def send_reset_password(self):
        full_name = self.__user.get_full_name()
        token = UserToken.create(user=self.__user, token_type=UserTokenConstrains.type_reset_password_token)
        url = self.__frontend_url + settings.REDIRECT_PATH_RESET_PASSWORD + '?token=' + token.token

        message = f'''
        Hello {full_name}
        Please click on link below to reset your password
        {url}
        This is an automatically generated message. Please do not reply to this email.
        '''

        html = render_to_string('reset-password.html', {
            'full_name': full_name,
            'url': url
        })

        return self.send(subject='Reset password', to=self.__user.email, html=html, text=message, reply=False)

    def send_magic_link(self):
        full_name = self.__user.get_full_name()
        token = UserToken.create(user=self.__user, token_type=UserTokenConstrains.type_magic_link_token)
        url = self.__frontend_url + settings.REDIRECT_PATH_MAGIC_LINK + '?token=' + token.token

        message = f'''
        Hello {full_name}
        Please click on link below to log in
        {url}
        This is an automatically generated message. Please do not reply to this email.
        '''

        html = render_to_string('magic-link.html', {
            'full_name': full_name,
            'url': url
        })

        return self.send(subject='Reset password', to=self.__user.email, html=html, text=message, reply=False)

