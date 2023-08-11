import time

from rest_framework.exceptions import ParseError, NotFound
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.serializers.auth_serializers import UserCreateSerializer, UserRegisterSerializer, UserSerializer


class CreateUserService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> UserCreateSerializer:
        """
            User registration
        """

        # Check and save input data
        user_serializer = UserRegisterSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        instance = user_serializer.save()

        # Convert data to a standard schema for a response
        user_serializer = UserSerializer(data=user_serializer.data, instance=instance)
        user_serializer.is_valid()

        # Formate response schema
        return_serializer = UserCreateSerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok',
                'result': user_serializer.data,
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class GetUserDetailsService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> UserSerializer:
        """
            Retrieve user profile
        """

        # Check input data
        try:
            pk = request.user.pk
        except:
            raise ParseError(f"Request must have 'user' parameter", code='id')
        try:
            instance = view.queryset.get(pk=pk)
        except:
            raise NotFound(f"User with id='{pk}' was not found", code='id')

        # Formate response schema
        user_serializer = UserSerializer(
            data={
                'id': instance.id,
                'username': instance.username,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
            },
            instance=instance
        )
        user_serializer.is_valid()

        return user_serializer


