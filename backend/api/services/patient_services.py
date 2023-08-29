import math
import time
from collections import OrderedDict
from datetime import datetime, date
from typing import List

from django.db import connections
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.models.egisz_db_models import VimisSending
from api.models.oncor_data_analytics_models import RcSms
from api.serializers.patient_serializers import PatientListSerializer, PatientDetailsSerializer, PatientSerializer
from api.serializers.serializers import PaginationListSerializer

from api.models.orientdb_engine import orient_db_client
from backend.settings import PAGE_SIZE


class GetPatientListService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> PatientListSerializer:
        """
            Retrieve list of patients
        """

        # Define queries
        query_body = """
            SELECT 
                @rid, 
                person.lastName as lastname, 
                person.firstName as firstname, 
                person.middleName as middlename, 
                person.birthDay.format('yyyy-MM-dd') as birthday,
                person.gender.value as gender, 
                person.snils as snils,
                tags.tags.tag as tags 
            FROM 
                ptn 
        """
        query_count_body = """
            SELECT 
                count(*) 
            FROM 
                ptn
        """

        # Get query params
        page = request.query_params.get('page', None)
        q = request.query_params.get('q', None)
        snils = request.query_params.get('snils', None)
        name = request.query_params.get('name', None)

        # Add filter to request
        if q:
            query_body += f"""
                WHERE
                   person.lastName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.firstName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.middleName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.snils LIKE "%{q}%"
            """
            query_count_body += f"""
                WHERE
                   person.lastName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.firstName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.middleName.toLowerCase() LIKE "%{q.lower()}%" OR  
                   person.snils LIKE "%{q}%"
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
                        WHERE
                           person.snils in ["{snils}", "{exp_snils}"]
                    """
                    query_count_body += f"""
                        WHERE
                           person.snils in ["{snils}", "{exp_snils}"]
                    """
                else:
                    query_body += f"""
                        WHERE
                           person.snils = "{snils}"
                    """
                    query_count_body += f"""
                        WHERE
                           person.snils = "{snils}"
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
                    WHERE
                       {condition}
                """
                query_count_body += f"""
                    WHERE
                       {condition}
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
                    ('base_diagnoses', get_patient_base_diagnoses(str(rec.oRecordData.get('rid', None)))),
                    ('semd_diagnoses', get_patient_semd_diagnoses(str(rec.oRecordData.get('rid', None)))),
                    ('tags', get_patient_tags(rec.oRecordData.get('tags', None))),
                ]
            )
            for rec in orient_result
        ]

        patient_list_serializer = view.get_serializer(result, many=True)

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


class GetPatientDetailsService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> PatientDetailsSerializer:
        """
            Retrieve detail of patient
        """

        # Check input data
        rid = kwargs.get("pk", None)
        if not rid:
            raise ParseError(f"Request must have 'rid' parameter", code='rid')

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
                tags.tags.tag as tags 
            FROM 
                ptn
            WHERE
               @rid = {rid}  
        """

        # Get queryset
        orient_result = orient_db_client.query(query_body, -1)
        if len(orient_result) != 1:
            raise NotFound(f"Patient with rid='{rid}' was not found", code='rid')

        result = \
            OrderedDict(
                [
                    ('rid', str(orient_result[0].oRecordData.get('rid', None))),
                    ('lastname', orient_result[0].oRecordData.get('lastname', None)),
                    ('firstname', orient_result[0].oRecordData.get('firstname', None)),
                    ('middlename', orient_result[0].oRecordData.get('middlename', None)),
                    ('birthday', orient_result[0].oRecordData.get('birthday', None)),
                    ('gender', orient_result[0].oRecordData.get('gender', None)),
                    ('snils', orient_result[0].oRecordData.get('snils', None)),
                    ('base_diagnoses', get_patient_base_diagnoses(str(orient_result[0].oRecordData.get('rid', None)))),
                    ('semd_diagnoses', get_patient_semd_diagnoses(str(orient_result[0].oRecordData.get('rid', None)))),
                    ('tags', get_patient_tags(orient_result[0].oRecordData.get('tags', None))),
                ]
            )

        # Convert data to a standard schema for a response
        patient_serializer = PatientSerializer(
            data=result
        )
        patient_serializer.is_valid()

        # Formate response schema
        return_serializer = PatientDetailsSerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok',
                'result': patient_serializer.data,
                'retExtInfo': '',
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


def get_patient_base_diagnoses(rid: str) -> List[OrderedDict]:
    result = [
        OrderedDict(
            [
                ('diagnosis_code', d_rec.oRecordData.get('mkb10', None)),
                ('diagnosis_name', d_rec.oRecordData.get('name', None)),
                ('diagnosis_date', d_rec.oRecordData.get('date', None)),
            ]
        )
        for d_rec in orient_db_client.query(
            f'''
            SELECT 
                diagnosis.registerDz.mkb10 as mkb10, 
                diagnosis.registerDz.name as name,
                timeRc.format('yyyy-MM-dd') as date 
            from 
                (SELECT 
                    EXPAND(records) 
                FROM 
                    ptn 
                WHERE 
                    @rid={rid}) 
            WHERE 
                @class="RcDz"
            ''',
            -1
        )
    ]
    result = sorted(result, key=lambda x: date.today() if x['diagnosis_date'] is None else x['diagnosis_date'])

    return result


def get_patient_semd_diagnoses(rid: str) -> List[OrderedDict]:
    # Define queries
    query_body = f"""
        SELECT 
            internalMessageId 
        FROM 
            (
                SELECT 
                    EXPAND(records) 
                FROM 
                    ptn 
                WHERE 
                    @rid={rid}
            ) 
        WHERE 
            @class="RcSMS"
    """

    # Get messages
    orient_result = orient_db_client.query(query_body, -1)
    messages = ["'" + rec.oRecordData.get('internalMessageId', '') + "'" for rec in orient_result]

    # Get message diagnoses
    message_diagnoses = None
    if messages:
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DOCINFO"]]/x:entry/x:observation/x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses1,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DOCINFO"]]/x:entry/x:observation[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]/x:effectiveTime/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses_time1,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]/x:entry/x:act/x:entryRelationship/x:observation/x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses2,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]/x:entry/x:act/x:entryRelationship/x:observation[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]/x:effectiveTime/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses_time2,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]/x:entry/x:observation/x:entryRelationship/x:observation/x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses3,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]/x:entry/x:observation/x:entryRelationship/x:observation[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]/x:effectiveTime/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses_time3,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="PLANSUR"]]/x:entry/x:observation/x:entryRelationship/x:act/x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses4,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="PLANSUR"]]/x:entry/x:observation/x:entryRelationship/x:act[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]/x:effectiveTime/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses_time4,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]/x:entry/x:observation/x:entryRelationship/x:observation/x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses5,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]/x:entry/x:observation/x:entryRelationship/x:observation[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]/x:effectiveTime/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as diagnoses_time5
            FROM
                vimis_sending
            WHERE
                internal_message_id in (""" + ','.join(messages) + ')'
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            message_diagnoses = cursor.fetchall()

    # Calculate diagnoses set
    diagnoses = set()
    if message_diagnoses:
        for message_diagnosis in message_diagnoses:
            for i in range(5):
                row_diagnoses = message_diagnosis[i * 2].split(',')
                row_diagnoses_time = message_diagnosis[i * 2 + 1].split(',')
                for n, diagnosis in enumerate(row_diagnoses):
                    if len(row_diagnoses) == len(row_diagnoses_time):
                        if diagnosis:
                            try:
                                dat = datetime(
                                    int(row_diagnoses_time[n][0:4]),
                                    int(row_diagnoses_time[n][4:6]),
                                    int(row_diagnoses_time[n][6:8])
                                ).date()
                            except:
                                dat = None
                            diagnoses = diagnoses.union({(diagnosis, dat)})
                    else:
                        if diagnosis:
                            diagnoses = diagnoses.union({(diagnosis, None)})

    # Formate result diagnoses list
    result = list()
    diagnoses = sorted(diagnoses, key=lambda x: x[0]+'None' if x[1] is None else x[0]+x[1].strftime("%Y%m%d"))
    previous_code = None
    for code, dat in diagnoses:
        if previous_code is None or previous_code != code:
            previous_code = code
            query_body = f"""
                SELECT
                    name
                FROM
                    directory
                WHERE
                    passport_oid = '1.2.643.5.1.13.13.11.1005' AND
                    code = '{code}'
                ORDER BY
                    version DESC
                """
            with connections['rosminzdrav-directories'].cursor() as cursor:
                cursor.execute(query_body)
                names = cursor.fetchall()
            result.append(OrderedDict([
                ('diagnosis_code', code),
                ('diagnosis_name', names[0][0]),
                ('diagnosis_date', dat)
            ]))
    result = sorted(result, key=lambda x: date.today() if x['diagnosis_date'] is None else x['diagnosis_date'])

    return result


def get_patient_tags(tags: list) -> List[OrderedDict]:
    result = [
        OrderedDict(
            [
                ('tag_rid', str(tag.oRecordData.get('rid', None))),
                ('tag_name', tag.oRecordData.get('name', None)),
                ('tag_description', tag.oRecordData.get('description', None)),
            ]
        )
        for tag in orient_db_client.query(
            f'''
            SELECT 
                @rid, 
                name,
                description 
            from 
                PtnTag 
            WHERE 
                @rid in [{','.join([str(rid) for rid in tags])}]
            ''',
            -1
        )
    ]

    return result
