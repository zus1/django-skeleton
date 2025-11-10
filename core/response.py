from django.http import JsonResponse
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict

class OkJsonResponse(JsonResponse):
    def __init__(self, data: dict, message: str = 'ok'):
        super().__init__(data={
        'message': message,
        'status': status.HTTP_200_OK,
        'data': data,
    }, status=status.HTTP_200_OK)

class CreatedJsonResponse(JsonResponse):
    def __init__(self, data: dict, message: str = 'created'):
        super().__init__(data={
        'message': message,
        'status': status.HTTP_201_CREATED,
        'data': data,
    }, status=status.HTTP_201_CREATED)

class BadRequestJsonResponse(JsonResponse):
    def __init__(self, message: str = 'bad request'):
        super().__init__(data={
        'message': message,
        'status': status.HTTP_400_BAD_REQUEST,
    },status=status.HTTP_400_BAD_REQUEST)

class NotFoundJsonResponse(JsonResponse):
    def __init__(self, data: dict | None = None, message: str = 'not found'):
        response = {
            'message': message,
            'status': status.HTTP_404_NOT_FOUND,
        }

        if data:
            response['data'] = data

        super().__init__(data=response, status=status.HTTP_404_NOT_FOUND)

class ValidationErrorJsonResponse(JsonResponse):
    def __init__(self, data: None | ReturnDict = None, message: str = 'validation error'):
        response = {
            'message': message,
            'status': status.HTTP_422_UNPROCESSABLE_ENTITY,
        }

        if data:
            response['data'] = data

        super().__init__(data=response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class ForbiddenJsonResponse(JsonResponse):
    def __init__(self, message: str = 'forbidden'):
        super().__init__(data={
            'message': message,
            'status': status.HTTP_403_FORBIDDEN,
    }, status=status.HTTP_403_FORBIDDEN)

class UnauthorizedJsonResponse(JsonResponse):
    def __init__(self, message: str = 'unauthorized'):
        super().__init__(data={
            'message': message,
            'status': status.HTTP_401_UNAUTHORIZED
        }, status=status.HTTP_401_UNAUTHORIZED)
