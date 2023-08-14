from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters.test_filters import CompanyFilter
from api.helpers import expand_dict
from api.models.test_models import Company
from api.permissions.permissions import FullPermission
from api.serializers.serializers import simple_responses
from api.serializers.test_serializars import CompanySerializer, CompanyListSerializer, CompanySingleEntrySerializer
from api.services.test_services import GetCompanyListService, CreateCompanyService, GetCompanyDetailsService, \
    UpdateCompanyService, DeleteCompanyService


@extend_schema(tags=['company'])
class CompanyViewSet(ModelViewSet):

    permission_classes = (FullPermission, )
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filterset_class = CompanyFilter

    @extend_schema(
        summary='Retrieve paginated and filtered list of companies',
        description='Retrieve paginated and filtered list of companies, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: CompanyListSerializer, }, simple_responses),
    )
    def list(self, request, *args, **kwargs):
        """
            Retrieve list of companies
        """
        company_list = GetCompanyListService.execute(request, self, *args, **kwargs)
        return Response(company_list.data)

    @extend_schema(
        summary='Create company',
        description='Create company, bla-bla-bla...',
        request=CompanySerializer,
        responses=expand_dict({status.HTTP_200_OK: CompanySingleEntrySerializer, }, simple_responses),
    )
    def create(self, request, *args, **kwargs):
        """
            Create company
        """
        company_create = CreateCompanyService.execute(request, self, *args, **kwargs)
        return Response(company_create.data)

    @extend_schema(
        summary='Retrieve company details',
        description='Retrieve company details, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: CompanySingleEntrySerializer, }, simple_responses),
    )
    def retrieve(self, request, *args, **kwargs):
        """
            Retrieve detail of company
        """
        company_details = GetCompanyDetailsService.execute(request, self, *args, **kwargs)
        return Response(company_details.data)

    @extend_schema(
        summary='Update company',
        description='Update company, bla-bla-bla...',
        request=CompanySerializer,
        responses=expand_dict({status.HTTP_200_OK: CompanySingleEntrySerializer, }, simple_responses),
    )
    def update(self, request, *args, **kwargs):
        """
            Update company
        """
        company_update = UpdateCompanyService.execute(request, self, *args, **kwargs)
        return Response(company_update.data)

    @extend_schema(
        summary='Delete company',
        description='Delete company, bla-bla-bla...',
        responses=expand_dict({status.HTTP_200_OK: CompanySingleEntrySerializer, }, simple_responses),
    )
    def destroy(self, request,  *args, **kwargs):
        """
            Delete company
        """
        company_delete = DeleteCompanyService.execute(request, self, *args, **kwargs)
        return Response(company_delete.data)


