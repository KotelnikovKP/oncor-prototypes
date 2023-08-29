from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.helpers import expand_dict
from api.models.orientdb_engine import Patient
from api.permissions.patient_permission import PatientPermission
from api.serializers.patient_serializers import PatientSerializer, PatientListSerializer, PatientDetailsSerializer
from api.serializers.serializers import simple_responses
from api.services.patient_services import GetPatientListService, GetPatientDetailsService


@extend_schema(tags=['Patient'])
class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()    # Fantom model (only for ModelViewSet)
    permission_classes = (PatientPermission,)
    serializer_class = PatientSerializer

    @extend_schema(
        summary='Retrieve paginated and filtered list of patients',
        description='Retrieve paginated and filtered list of patients, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: PatientListSerializer, }, simple_responses),
        parameters=[
            OpenApiParameter('q', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             description='Patient name or snils for result set filtering '
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
    def list(self, request: Request, *args, **kwargs):
        """
            Retrieve list of patients
        """
        patient_list = GetPatientListService.execute(request, self, *args, **kwargs)
        return Response(patient_list.data)

    @extend_schema(
        summary='Retrieve detail of patient',
        description='Retrieve detail of patient, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: PatientDetailsSerializer, }, simple_responses),
    )
    def retrieve(self, request, *args, **kwargs):
        """
            Retrieve detail of patient
        """
        patient_details = GetPatientDetailsService.execute(request, self, *args, **kwargs)
        return Response(patient_details.data)

    # @extend_schema(
    #     summary='Retrieve diagnoses of patient',
    #     description='Retrieve diagnoses of patient, bla-bla-bla...',
    #     responses=expand_dict({status.HTTP_200_OK: PatientDiagnosisListSerializer, }, simple_responses),
    # )
    # @action(detail=True)
    # def diagnoses(self, request, *args, **kwargs):
    #     """
    #         Retrieve diagnoses of patient
    #     """
    #     patient_diagnoses = GetPatientDiagnosesService.execute(request, self, *args, **kwargs)
    #     return Response(patient_diagnoses.data)
    #
    # @extend_schema(
    #     summary='Retrieve medical cards of patient',
    #     description='Retrieve medical cards of patient, bla-bla-bla...',
    #     responses=expand_dict({status.HTTP_200_OK: PatientMedicalCardListSerializer, }, simple_responses),
    # )
    # @action(detail=True)
    # def medical_cards(self, request, *args, **kwargs):
    #     """
    #         Retrieve medical cards of patient
    #     """
    #     patient_medical_cards = GetPatientMedicalCardsService.execute(request, self, *args, **kwargs)
    #     return Response(patient_medical_cards.data)
    #
    # @extend_schema(
    #     summary='Retrieve SEMDs of patient',
    #     description='Retrieve SEMDs of patient, bla-bla-bla...',
    #     responses=expand_dict({status.HTTP_200_OK: SEMDListSerializer, }, simple_responses),
    #     parameters=[OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY,
    #                                  description='A page number within the paginated result set.')] +
    #     SEMDFilter.get_api_filters(),
    # )
    # @action(detail=True)
    # def semds(self, request, *args, **kwargs):
    #     """
    #         Retrieve SEMD list of patient
    #     """
    #     patient_semds = GetPatientSemdsService.execute(request, self, *args, **kwargs)
    #     return Response(patient_semds.data)
    #
    # @extend_schema(
    #     summary='Retrieve laboratory tests of patient',
    #     description='Retrieve laboratory tests of patient, bla-bla-bla...',
    #     responses=expand_dict({status.HTTP_200_OK: SemdTestListSerializer, }, simple_responses),
    #     parameters=[OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY,
    #                                  description='A page number within the paginated result set.')] +
    #     SemdTestFilter.get_api_filters(),
    # )
    # @action(detail=True)
    # def tests(self, request, *args, **kwargs):
    #     """
    #         Retrieve laboratory tests of patient
    #     """
    #     patient_semd_tests = GetPatientSemdTestsService.execute(request, self, *args, **kwargs)
    #     return Response(patient_semd_tests.data)
    #
    # @extend_schema(
    #     summary='Retrieve registry report of patient',
    #     description='Retrieve registry report of patient, bla-bla-bla...',
    #     responses=expand_dict({status.HTTP_200_OK: PatientRegistryReportDetailSerializer, }, simple_responses),
    #     parameters=[
    #         OpenApiParameter('diagnosis_registry_id', OpenApiTypes.STR, OpenApiParameter.QUERY,
    #                          description='Diagnosis registry id for result set filtering.')
    #     ],
    # )
    # @action(detail=True)
    # def registry_report(self, request, *args, **kwargs):
    #     """
    #         Retrieve registry report of patient
    #     """
    #     patient_registry_report = GetPatientRegistryReportService.execute(request, self, *args, **kwargs)
    #     return Response(patient_registry_report.data)
