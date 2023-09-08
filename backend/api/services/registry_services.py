import math
import time
from collections import OrderedDict

from django.db.models import Exists, OuterRef
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.models.orientdb_engine import orient_db_client
from api.serializers.patient_serializers import PatientListSerializer, PatientSerializer
from api.serializers.registry_serializers import DiagnosisRegistryListSerializer, DiagnosisRegistrySerializer, \
    DiagnosisRegistrySingleEntrySerializer
from api.serializers.serializers import PaginationListSerializer
from api.services.patient_services import get_patient_semd_diagnoses, get_patient_base_diagnoses, get_patient_tags
from backend.settings import PAGE_SIZE


class GetDiagnosisRegistryListService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> DiagnosisRegistryListSerializer:
        """
            Retrieve list of diagnosis registry
        """

        # Filter queryset
        queryset = view.filter_queryset(view.get_queryset())

        # Paginate queryset
        page = view.paginate_queryset(queryset)
        if page is None:
            diagnosis_registry_list_serializer = view.get_serializer(queryset, many=True)
            count = view.paginator.count
            items_per_page = view.paginator.per_page
            start_item_index = 0 if count == 0 else 1
            end_item_index = count
            previous_page = None
            current_page = 1
            next_page = None
        else:
            diagnosis_registry_list_serializer = view.get_serializer(page, many=True)
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
        return_serializer = DiagnosisRegistryListSerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok' if count > 0 else 'Result set is empty',
                'result': diagnosis_registry_list_serializer.data,
                'retExtInfo': pagination_list_serializer.data,
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class CreateDiagnosisRegistryService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> DiagnosisRegistrySingleEntrySerializer:
        """
            Create diagnosis registry
        """

        # Check and save input data
        diagnosis_registry_serializer = DiagnosisRegistrySerializer(data=request.data)
        diagnosis_registry_serializer.is_valid(raise_exception=True)
        diagnosis_registry_serializer.save()

        # Formate response schema
        return_serializer = DiagnosisRegistrySingleEntrySerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok',
                'result': diagnosis_registry_serializer.data,
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class GetDiagnosisRegistryDetailsService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> DiagnosisRegistrySingleEntrySerializer:
        """
            Retrieve detail of diagnosis registry
        """

        # Check input data
        pk = kwargs.get("pk", None)
        if not pk:
            raise ParseError(f"Request must have 'id' parameter", code='id')
        try:
            instance = view.queryset.get(pk=pk)
        except:
            raise NotFound(f"Diagnosis registry with id='{pk}' was not found", code='id')

        # Convert data to a standard schema for a response
        diagnosis_registry_serializer = DiagnosisRegistrySerializer(
            data={
                'id': instance.id,
                'name': instance.name,
                'short_name': instance.short_name,
                'oncor_tag_rid': instance.oncor_tag_rid,
                'medical_record_transcript_settings': instance.medical_record_transcript_settings,
            },
            instance=instance
        )
        diagnosis_registry_serializer.is_valid()

        # Formate response schema
        return_serializer = DiagnosisRegistrySingleEntrySerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok',
                'result': diagnosis_registry_serializer.data,
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class UpdateDiagnosisRegistryService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> DiagnosisRegistrySingleEntrySerializer:
        """
            Update diagnosis registry
        """

        # Check and save input data
        pk = kwargs.get("pk", None)
        if not pk:
            raise ParseError(f"Request must have 'id' parameter", code='id')
        try:
            instance = view.queryset.get(pk=pk)
        except:
            raise NotFound(f"Diagnosis registry with id='{pk}' was not found", code='id')

        diagnosis_registry_serializer = DiagnosisRegistrySerializer(data=request.data, instance=instance)
        diagnosis_registry_serializer.is_valid(raise_exception=True)
        diagnosis_registry_serializer.save()

        # Formate response schema
        is_data = request.data.get('name', None) is not None or \
            request.data.get('short_name', None) is not None or \
            request.data.get('oncor_tag_rid', None) is not None or \
            request.data.get('medical_record_transcript_settings', None) is not None
        return_serializer = DiagnosisRegistrySingleEntrySerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok' if is_data else 'You changed nothing',
                'result': diagnosis_registry_serializer.data,
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class DeleteDiagnosisRegistryService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> DiagnosisRegistrySingleEntrySerializer:
        """
            Delete diagnosis registry
        """

        # Check input data
        pk = kwargs.get("pk", None)
        if not pk:
            raise ParseError(f"Request must have 'id' parameter", code='id')
        try:
            instance = view.queryset.get(pk=pk)
        except:
            raise NotFound(f"Diagnosis registry with id='{pk}' was not found", code='id')

        # Delete diagnosis registry
        instance.delete()

        # Formate response schema
        return_serializer = DiagnosisRegistrySingleEntrySerializer(
            data={
                'retCode': 0,
                'retMsg': f'Ok. Diagnosis registry with id={pk} was deleted',
                'result': {},
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


class GetDiagnosisRegistryPatientsService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> PatientListSerializer:
        """
            Retrieve patient list of diagnosis registry
        """

        # Check input data
        pk = kwargs.get("pk", None)
        if not pk:
            raise ParseError(f"Request must have 'id' parameter", code='id')
        try:
            instance = view.queryset.get(pk=pk)
        except:
            raise NotFound(f"Diagnosis registry with id='{pk}' was not found", code='id')

        # Define queries
        query_body = f"""
            SELECT 
                @rid, 
                person.lastName as lastname, 
                person.firstName as firstname, 
                person.middleName as middlename, 
                person.birthDay.format('yyyy-MM-dd') as birthday,
                person.gender.value as gender, 
                person.snils as snils,
                tags.tags.tag as tags,
                observer.nsiMedOrg.oid as mo_oid,
                observer.nsiMedOrg.name as mo_name,
                person.address.medTerr.name as med_terr,
                person.address.livingAreaType.rbps.S_NAME.value as living_area_type,
                person.phones as phones,
                person.address.locality.type as locality_type,
                person.address.locality.name as locality_name,
                person.address.address as address 
            FROM 
                ptn
            WHERE
                tags.tags CONTAINS(tag = {instance.oncor_tag_rid})
        """
        query_count_body = f"""
            SELECT 
                count(*) 
            FROM 
                ptn
            WHERE
                tags.tags CONTAINS(tag = {instance.oncor_tag_rid})
        """

        # Get query params
        page = request.query_params.get('page', None)
        q = request.query_params.get('q', None)
        snils = request.query_params.get('snils', None)
        name = request.query_params.get('name', None)

        # Add filter to request
        if q:
            query_body += f"""
                AND
                   (person.lastName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.firstName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.middleName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.snils LIKE "%{q}%")
            """
            query_count_body += f"""
                AND
                   (person.lastName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.firstName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.middleName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.snils LIKE "%{q}%")
            """
        else:
            if snils:
                exp_snils = None
                if len(snils) == 11:
                    exp_snils = snils[0:3] + '-' + snils[3:6] + '-' + snils[6:9] + ' ' + snils[9:]
                elif len(snils) == 14:
                    exp_snils = snils
                    snils = snils[0:3] + snils[4:7] + snils[8:11] + snils[12:]
                if exp_snils:
                    query_body += f"""
                        AND person.snils in ["{snils}", "{exp_snils}"]
                    """
                    query_count_body += f"""
                        AND person.snils in ["{snils}", "{exp_snils}"]
                    """
                else:
                    query_body += f"""
                        AND person.snils = "{snils}"
                    """
                    query_count_body += f"""
                        AND person.snils = "{snils}"
                    """
            elif name:
                names = name.split(' ')
                lastname = names[0]
                condition = f'person.lastName.toLowerCase() = "{lastname.lower()}"'
                if len(names) > 1:
                    firstname = names[1]
                    condition += f' AND person.firstName.toLowerCase() = "{firstname.lower()}"'
                if len(names) > 2:
                    middlename = names[2]
                    condition += f' AND person.middleName.toLowerCase() = "{middlename.lower()}"'
                query_body += f"""
                    AND {condition}
                """
                query_count_body += f"""
                    AND {condition}
                """

        # Calculate count of queryset
        orient_result = orient_db_client.query(query_count_body, -1)
        count = orient_result[0].count

        # Add paginate to request
        if page is not None:
            try:
                page = int(page)
                page = page if page >= 1 else 1
                page = page if page <= math.ceil(count / PAGE_SIZE) else math.ceil(count / PAGE_SIZE)
            except:
                page = 1
        else:
            page = 1

        query_body += f"""
            SKIP {(page - 1) * PAGE_SIZE}
            LIMIT {PAGE_SIZE}
        """

        # Get queryset
        orient_result = orient_db_client.query(query_body, -1)
        result = [
            OrderedDict(
                [
                    ('rid', str(rec.oRecordData.get('rid', None))),
                    ('lastname', rec.oRecordData.get('lastname', None)),
                    ('firstname', rec.oRecordData.get('firstname', None)),
                    ('middlename', rec.oRecordData.get('middlename', None)),
                    ('birthday', rec.oRecordData.get('birthday', None)),
                    ('gender', rec.oRecordData.get('gender', None)),
                    ('snils', rec.oRecordData.get('snils', None)),
                    ('mo_oid', rec.oRecordData.get('mo_oid', None)),
                    ('mo_name', rec.oRecordData.get('mo_name', None)),
                    ('med_terr', rec.oRecordData.get('med_terr', None)),
                    ('living_area_type', rec.oRecordData.get('living_area_type', None)),
                    ('phones', rec.oRecordData.get('phones', None)),
                    ('address', OrderedDict(
                        [
                            ('locality_type', rec.oRecordData.get('locality_type', None)),
                            ('locality_name', rec.oRecordData.get('locality_name', None)),
                            ('address', rec.oRecordData.get('address', None)),
                        ]
                    )),
                    ('base_diagnoses', get_patient_base_diagnoses(str(rec.oRecordData.get('rid', None)))),
                    ('semd_diagnoses', get_patient_semd_diagnoses(str(rec.oRecordData.get('rid', None)))),
                    ('tags', get_patient_tags(rec.oRecordData.get('tags', None))),
                ]
            )
            for rec in orient_result
        ]
        patient_list_serializer = PatientSerializer(result, many=True)

        items_per_page = PAGE_SIZE
        start_item_index = 0 if count == 0 else (page - 1) * PAGE_SIZE + 1
        end_item_index = (page - 1) * PAGE_SIZE - 1 + len(orient_result) + 1
        previous_page = page - 1 if page > 1 else None
        current_page = page
        next_page = page + 1 if page < math.ceil(count / PAGE_SIZE) else None

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
        return_serializer = PatientListSerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok' if count > 0 else 'Result set is empty',
                'result': patient_list_serializer.data,
                'retExtInfo': pagination_list_serializer.data,
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer
