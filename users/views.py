from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.http import JsonResponse
from rest_framework.exceptions import NotFound, APIException, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core import response
from core.exception import NotVerboseValidationError
from users.constant import UserTokenConstrains
from users.dto import LoginResponseFactory
from users.email import UserEmail
from users.models import User, UserToken
from users.repo import UserRepository, UserTokenRepository
from django.core.exceptions import ValidationError as CoreValidationError

from users.serializers import RegisterInSerializer, ResetPasswordSerializer, LoginSerializer, \
    RegisterOutSerializer, MeSerializer


class Register(APIView):
    serializer_in_class = RegisterInSerializer
    serializer_out_class = RegisterOutSerializer

    def post(self, request):
        in_serializer = self.serializer_in_class(data=request.data)
        if not in_serializer.is_valid():
            return response.ValidationErrorJsonResponse(data=in_serializer.errors)

        try:
            user = in_serializer.save()
        except CoreValidationError as e:
            return response.ValidationErrorJsonResponse(message=str(e))

        try:
            UserEmail(user=user).send_email_verification()
        except Exception:
            pass #Catch any unexpected errors, not to brake main flow

        out_serializer = self.serializer_out_class(user)

        return response.CreatedJsonResponse(data=out_serializer.data)

class VerifyResend(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return response.BadRequestJsonResponse(message='email is missing')

        user = User.objects.filter(email=email).first()
        if not user:
            return response.NotFoundJsonResponse(message='user not found')

        sent = UserEmail(user=user).send_email_verification()

        return response.OkJsonResponse(data={
            'sent': sent,
        })

class Verify(APIView):
    def patch(self, request):
        token_string = request.query_params.get('token', None)
        if not token_string:
            return response.BadRequestJsonResponse(message='token is missing')

        try:
            user_token = UserTokenRepository(request=request).find_token_by_token_string(token_string)
        except (NotFound, NotVerboseValidationError) as e:
            return JsonResponse({
                'status': e.status_code,
                'message': str(e),
            }, status=e.status_code)


        user = UserRepository(request=request).activate(user=user_token.user)
        UserTokenRepository(request=request).make_as_used(token=user_token)

        return response.OkJsonResponse(data={
            'verified': user.is_active,
        })

class ResetPasswordSend(APIView):
    def post(self, request):
        email = request.data.get('email', None)
        if not email:
            return response.BadRequestJsonResponse(message='email is missing')

        user = User.objects.filter(email=email).first()
        if not user:
            return response.NotFoundJsonResponse(message='user not found')

        sent = UserEmail(user=user).send_reset_password()

        return response.OkJsonResponse(data={
            'sent': sent,
        })

class ResetPassword(APIView):
    serializer_class = ResetPasswordSerializer

    def patch(self, request):
        token_string = request.query_params.get('token', None)
        if not token_string:
            return response.BadRequestJsonResponse(message='token is missing')

        try:
            user_token = UserTokenRepository(request=request).find_token_by_token_string(token_string=token_string)
        except (NotFound, APIException) as e:
            return JsonResponse({
                'status': e.status_code,
                'message': e.detail,
            }, status=e.status_code)

        user = user_token.user
        serializer = self.serializer_class(data=request.data, context={"user": user})
        if not serializer.is_valid():
            return response.ValidationErrorJsonResponse(data=serializer.errors)

        try:
            UserRepository(request=request).reset_password(user=user, data=serializer.validated_data)
        except CoreValidationError as e:
            return response.ValidationErrorJsonResponse(message=str(e))

        UserTokenRepository(request=request).make_as_used(token=user_token)

        return response.OkJsonResponse(data={
            'password_reset': True,
        })

class MagicLinkSend(APIView):
    def post(self, request):
        email = request.data.get('email', None)
        if not email:
            return response.BadRequestJsonResponse(message='email is missing')

        user = User.objects.filter(email=email).first()
        if not user:
            return response.NotFoundJsonResponse(message='user not found')

        sent = UserEmail(user=user).send_magic_link()

        return response.OkJsonResponse(data={
            'sent': sent,
        })

class MagicLinkLogin(APIView):
    def post(self, request):
        token_string = request.query_params.get('token', None)
        if not token_string:
            return response.BadRequestJsonResponse(message='token is missing')

        try:
            user_token = UserTokenRepository(request=request).find_token_by_token_string(token_string=token_string)
        except (NotFound, APIException) as e:
            return JsonResponse({
                'status': e.status_code,
                'message': e.detail,
            })

        login(request=request, user=user_token.user)

        UserTokenRepository(request=request).make_as_used(token=user_token)

        return response.OkJsonResponse(data=LoginResponseFactory.create(user=user_token.user).to_dict())

class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return response.ValidationErrorJsonResponse(data=serializer.errors)

        base_user = authenticate(
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        if base_user is None:
            return response.ForbiddenJsonResponse(message='invalid credentials')

        user = User.objects.filter(email=serializer.validated_data['email']).first()
        login(request=request, user=user)

        return response.OkJsonResponse(data=LoginResponseFactory.create(user=user).to_dict())

class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        token: UserToken = request.auth
        if not token:
            return response.NotFoundJsonResponse(message='token is missing')

        token_deleted = UserToken.objects.filter(
            user=request.user,
            type=UserTokenConstrains.type_access_token,
            token=token.token
        ).delete()

        logout(request=request)

        return response.OkJsonResponse(data={
            'logged_out': token_deleted[0] > 0
        })

class Me(APIView):
    serializer_class = MeSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = self.serializer_class(request.user)

        return response.OkJsonResponse(data=serializer.data)

class MeAvatar(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        old_avatar = str(user.avatar)

        user.avatar = request.FILES['avatar']

        try:
            user.clean_fields()
        except ValidationError as e:
            return response.ValidationErrorJsonResponse(message=e.detail)

        user.save()

        if old_avatar and str(user.avatar) != old_avatar:
            default_storage.delete(name=old_avatar)

        return response.CreatedJsonResponse(data={
            'avatar': default_storage.url(name=str(user.avatar)),
        })




