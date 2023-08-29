from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters.registry_filters import DiagnosisRegistryFilter
from api.helpers import expand_dict
from api.models.registry_models import DiagnosisRegistry
from api.permissions.registry_permission import DiagnosisRegistryPermission
from api.serializers.patient_serializers import PatientListSerializer
from api.serializers.registry_serializers import DiagnosisRegistrySerializer, DiagnosisRegistryListSerializer, \
    DiagnosisRegistrySingleEntrySerializer
from api.serializers.serializers import simple_responses
from api.services.registry_services import GetDiagnosisRegistryListService, CreateDiagnosisRegistryService, \
    GetDiagnosisRegistryDetailsService, UpdateDiagnosisRegistryService, DeleteDiagnosisRegistryService, \
    GetDiagnosisRegistryPatientsService


@extend_schema(tags=['Diagnosis registry'])
class DiagnosisRegistryViewSet(ModelViewSet):

    permission_classes = (DiagnosisRegistryPermission, )
    queryset = DiagnosisRegistry.objects.all()
    serializer_class = DiagnosisRegistrySerializer
    filterset_class = DiagnosisRegistryFilter

    @extend_schema(
        summary='Retrieve paginated and filtered list of diagnosis registers',
        description='Retrieve paginated and filtered list of diagnosis registers, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: DiagnosisRegistryListSerializer, }, simple_responses),
    )
    def list(self, request, *args, **kwargs):
        """
            Retrieve list of diagnosis registers
        """
        diagnosis_registry_list = GetDiagnosisRegistryListService.execute(request, self, *args, **kwargs)
        return Response(diagnosis_registry_list.data)

    @extend_schema(
        summary='Create diagnosis registry',
        description='Create diagnosis registry, bla-bla-bla...',
        request=DiagnosisRegistrySerializer,
        responses=expand_dict({status.HTTP_200_OK: DiagnosisRegistrySingleEntrySerializer, }, simple_responses),
    )
    def create(self, request, *args, **kwargs):
        """
            Create diagnosis registry
        """
        diagnosis_registry_create = CreateDiagnosisRegistryService.execute(request, self, *args, **kwargs)
        return Response(diagnosis_registry_create.data)

    @extend_schema(
        summary='Retrieve diagnosis registry details',
        description='Retrieve diagnosis registry details, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: DiagnosisRegistrySingleEntrySerializer, }, simple_responses),
    )
    def retrieve(self, request, *args, **kwargs):
        """
            Retrieve detail of diagnosis registry
        """
        diagnosis_registry_details = GetDiagnosisRegistryDetailsService.execute(request, self, *args, **kwargs)
        return Response(diagnosis_registry_details.data)

    @extend_schema(
        summary='Update diagnosis registry',
        description='Update diagnosis registry, bla-bla-bla...',
        request=DiagnosisRegistrySerializer,
        responses=expand_dict({status.HTTP_200_OK: DiagnosisRegistrySingleEntrySerializer, }, simple_responses),
    )
    def update(self, request, *args, **kwargs):
        """
            Update diagnosis registry
        """
        diagnosis_registry_update = UpdateDiagnosisRegistryService.execute(request, self, *args, **kwargs)
        return Response(diagnosis_registry_update.data)

    @extend_schema(
        summary='Delete diagnosis registry',
        description='Delete diagnosis registry, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: DiagnosisRegistrySingleEntrySerializer, }, simple_responses),
    )
    def destroy(self, request,  *args, **kwargs):
        """
            Delete diagnosis registry
        """
        diagnosis_registry_delete = DeleteDiagnosisRegistryService.execute(request, self, *args, **kwargs)
        return Response(diagnosis_registry_delete.data)

    @extend_schema(
        summary='Retrieve paginated and filtered patients list of diagnosis registry',
        description='Retrieve paginated and filtered patients list of diagnosis registry, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: PatientListSerializer, }, simple_responses),
        parameters=[
            OpenApiParameter('q', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description='Patient lastname or snils for result set filtering '
                                         '(by content case insensitive).'),
            OpenApiParameter('snils', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description='Patient snils for result set filtering.'),
            OpenApiParameter('name', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description='Patient name for result set filtering '
                                         '(by content case insensitive).'),
            OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description='A page number within the paginated result set.'),
        ],
    )
    @action(detail=True)
    def patients(self, request, *args, **kwargs):
        """
            Retrieve paginated and filtered patients list of diagnosis registry
        """
        diagnosis_registry_patients = GetDiagnosisRegistryPatientsService.execute(request, self, *args, **kwargs)
        return Response(diagnosis_registry_patients.data)
