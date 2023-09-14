from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.utils.base_utils import expand_dict
from api.serializers.auth_serializers import UserRegisterSerializer, UserCreateSerializer, UserDetailsSerializer
from api.serializers.serializers import simple_responses
from api.services.auth_services import CreateUserService, GetUserDetailsService


@extend_schema(tags=['Auth'])
@extend_schema_view(
    post=extend_schema(
        summary='Authorize user and retrieve an access token',
        description='Authorize user and retrieve a bearer token, bla-bla-bla...',
    ),
)
class SemdCustomTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=['Auth'])
@extend_schema_view(
    post=extend_schema(
        summary='Refresh token',
        description='Refresh token, bla-bla-bla...',
    ),
)
class SemdCustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=['Auth'])
class UserRegisterViewSet(ModelViewSet):
    permission_classes = (AllowAny, )
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    @extend_schema(
        summary='Register user',
        description='Register user, bla-bla-bla...',
        request=UserRegisterSerializer(many=False),
        responses=expand_dict({status.HTTP_200_OK: UserCreateSerializer, }, simple_responses),
    )
    def create(self, request, *args, **kwargs):
        """
            User registration
        """
        user_create = CreateUserService.execute(request, self, *args, **kwargs)
        return Response(user_create.data)

    @extend_schema(
        summary='Retrieve user profile',
        description='Retrieve user profile, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: UserDetailsSerializer, }, simple_responses),
    )
    def retrieve(self, request, *args, **kwargs):
        """
            Retrieve user profile
        """
        user_details = GetUserDetailsService.execute(request, self, *args, **kwargs)
        return Response({"user": user_details.data})
