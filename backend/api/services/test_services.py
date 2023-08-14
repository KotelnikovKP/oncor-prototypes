import time

from rest_framework.exceptions import ParseError, NotFound
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.serializers.serializers import PaginationListSerializer
from api.serializers.test_serializars import CompanyListSerializer, CompanySingleEntrySerializer, CompanySerializer


class GetCompanyListService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> CompanyListSerializer:
        """
            Retrieve list of company
        """

        # Filter queryset
        queryset = view.filter_queryset(view.get_queryset())

        # Paginate queryset
        page = view.paginate_queryset(queryset)
        if page is None:
            company_list_serializer = view.get_serializer(queryset, many=True)
            count = view.paginator.count
            items_per_page = view.paginator.per_page
            start_item_index = 0 if count == 0 else 1
            end_item_index = count
            previous_page = None
            current_page = 1
            next_page = None
        else:
            company_list_serializer = view.get_serializer(page, many=True)
            count = view.paginator.page.paginator.count
            items_per_page = view.paginator.page.paginator.per_page
            start_item_index = view.paginator.page.start_index()
            end_item_index = view.paginator.page.end_index()
            previous_page = view.paginator.page.previous_page_number() if view.paginator.page.has_previous() else None
            current_page = view.paginator.page.number
            next_page = view.paginator.page.next_page_number() if view.paginator.page.has_next() else None

        # Formate pagination list's extra information schema
        pagination_list_serializer = PaginationListSerializer(
            data={
                'count_items': count,
                'items_per_page': items_per_page,
                'start_item_index': start_item_index,
                'end_item_index': end_item_index,
                'previous_page': previous_page,
                'current_page': current_page,
                'next_page': next_page,
            }
        )
        pagination_list_serializer.is_valid()

        # Formate response schema
        return_serializer = CompanyListSerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok' if count > 0 else 'Result set is empty',
                'result': company_list_serializer.data,
                'retExtInfo': pagination_list_serializer.data,
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class CreateCompanyService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> CompanySingleEntrySerializer:
        """
            Create company
        """

        # Check and save input data
        company_serializer = CompanySerializer(data=request.data)
        company_serializer.is_valid(raise_exception=True)
        company_serializer.save()

        # Formate response schema
        return_serializer = CompanySingleEntrySerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok',
                'result': company_serializer.data,
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class GetCompanyDetailsService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> CompanySingleEntrySerializer:
        """
            Retrieve detail of company
        """

        # Check input data
        pk = kwargs.get("pk", None)
        if not pk:
            raise ParseError(f"Request must have 'id' parameter", code='id')
        try:
            instance = view.queryset.get(pk=pk)
        except:
            raise NotFound(f"Company with id='{pk}' was not found", code='id')

        # Convert data to a standard schema for a response
        company_serializer = CompanySerializer(
            data={
                'id': instance.id,
                'name': instance.name,
                'email': instance.email,
                'is_active': instance.is_active,
                'is_deleted': instance.is_deleted,
            },
            instance=instance
        )
        company_serializer.is_valid()

        # Formate response schema
        return_serializer = CompanySingleEntrySerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok',
                'result': company_serializer.data,
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class UpdateCompanyService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> CompanySingleEntrySerializer:
        """
            Update company
        """

        # Check and save input data
        pk = kwargs.get("pk", None)
        if not pk:
            raise ParseError(f"Request must have 'id' parameter", code='id')
        try:
            instance = view.queryset.get(pk=pk)
        except:
            raise NotFound(f"Company with id='{pk}' was not found", code='id')

        company_serializer = CompanySerializer(data=request.data, instance=instance)
        company_serializer.is_valid(raise_exception=True)
        company_serializer.save()

        # Formate response schema
        is_data = request.data.get('name', None) is not None or \
            request.data.get('email', None) is not None or \
            request.data.get('is_active', None) is not None or \
            request.data.get('is_deleted', None) is not None
        return_serializer = CompanySingleEntrySerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok' if is_data else 'You changed nothing',
                'result': company_serializer.data,
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class DeleteCompanyService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> CompanySingleEntrySerializer:
        """
            Delete company
        """

        # Check input data
        pk = kwargs.get("pk", None)
        if not pk:
            raise ParseError(f"Request must have 'id' parameter", code='id')
        try:
            instance = view.queryset.get(pk=pk)
        except:
            raise NotFound(f"Company with id='{pk}' was not found", code='id')

        # Delete company
        instance.delete()

        # Formate response schema
        return_serializer = CompanySingleEntrySerializer(
            data={
                'retCode': 0,
                'retMsg': f'Ok. company with id={pk} was deleted',
                'result': {},
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


