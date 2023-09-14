from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.services.order_services.order_F14v2_services import GetF14v2Service
from api.utils.base_utils import expand_dict
from api.models.orientdb_engine import Patient
from api.permissions.permissions import OnlyListPermission
from api.serializers.order_serializers import F14ListSerializer, F14Serializer, F14v2Serializer, F14v2ListSerializer
from api.serializers.serializers import simple_responses
from api.services.order_services.order_F14_services import GetF14Service


@extend_schema(tags=['Orders reports'])
class F14ViewSet(ModelViewSet):
    queryset = Patient.objects.all()    # Fantom model (only for ModelViewSet)
    permission_classes = (OnlyListPermission,)
    serializer_class = F14Serializer

    @extend_schema(
        summary='Retrieve orders F14 report',
        description='Retrieve orders F14 report, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: F14ListSerializer, }, simple_responses),
        parameters=[
            OpenApiParameter('date_from', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description='Orders F14 report period date from condition.'),
            OpenApiParameter('date_to', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description='Orders F14 report period date to condition.'),
        ],
    )
    def list(self, request: Request, *args, **kwargs):
        """
            Retrieve orders F14 report
        """
        f14_list = GetF14Service.execute(request, self, *args, **kwargs)
        return Response(f14_list.data)


@extend_schema(tags=['Orders reports'])
class F14v2ViewSet(ModelViewSet):
    queryset = Patient.objects.all()    # Fantom model (only for ModelViewSet)
    permission_classes = (OnlyListPermission,)
    serializer_class = F14v2Serializer

    @extend_schema(
        summary='Retrieve orders F14 v.2 report',
        description='Retrieve orders F14 v.2 report, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: F14v2ListSerializer, }, simple_responses),
        parameters=[
            OpenApiParameter('date_from', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description='Orders F14 report period date from condition.'),
            OpenApiParameter('date_to', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description='Orders F14 report period date to condition.'),
        ],
    )
    def list(self, request: Request, *args, **kwargs):
        """
            Retrieve orders F14 v.2 report
        """
        f14v2_list = GetF14v2Service.execute(request, self, *args, **kwargs)
        return Response(f14v2_list.data)
