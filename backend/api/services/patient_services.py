import math
import time
from collections import OrderedDict
from datetime import datetime, date
from html import unescape
from typing import List

import xmltodict
from django.db import connections
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.serializers.patient_serializers import PatientListSerializer, PatientDetailsSerializer, PatientSerializer, \
    PatientListDiagnosisSerializer, PatientDiagnosisSerializer
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
                person.code as code, 
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
                    ('code', rec.oRecordData.get('code', None)),
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
                person.code as code,
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
                    ('code', orient_result[0].oRecordData.get('code', None)),
                    ('snils', orient_result[0].oRecordData.get('snils', None)),
                    ('mo_oid', orient_result[0].oRecordData.get('mo_oid', None)),
                    ('mo_name', orient_result[0].oRecordData.get('mo_name', None)),
                    ('med_terr', orient_result[0].oRecordData.get('med_terr', None)),
                    ('living_area_type', orient_result[0].oRecordData.get('living_area_type', None)),
                    ('phones', orient_result[0].oRecordData.get('phones', None)),
                    ('address', OrderedDict(
                        [
                            ('locality_type', orient_result[0].oRecordData.get('locality_type', None)),
                            ('locality_name', orient_result[0].oRecordData.get('locality_name', None)),
                            ('address', orient_result[0].oRecordData.get('address', None)),
                        ]
                    )),
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
                ('diagnosis_first_date', d_rec.oRecordData.get('date', None)),
                ('diagnosis_first_kind_code', ''),
                ('diagnosis_first_kind_name', ''),
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
    result = \
        sorted(result, key=lambda x: date.today() if x['diagnosis_first_date'] is None else x['diagnosis_first_date'])

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
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:observation[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]', payload::xml, '{{x,urn:hl7-org:v3}}'), '<new/>'), '\n', ' ', 'g') as diagnoses
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
            xmls = message_diagnosis[0].split('<new/>')
            for xml in xmls:
                if xml:
                    try:
                        row_diagnosis = None
                        row_diagnosis_name = None
                        row_diagnosis_time = None
                        row_diagnosis_kind_code = None
                        row_diagnosis_kind_name = None
                        observation = xmltodict.parse(xml)['observation']
                        observation_values = observation.get('value', None)
                        if observation_values:
                            if isinstance(observation_values, dict):
                                observation_values = [observation_values]
                            for observation_value in observation_values:
                                if isinstance(observation_value, dict):
                                    observation_value_code_system = observation_value.get('@codeSystem', '')
                                    if observation_value_code_system == '1.2.643.5.1.13.13.11.1005':
                                        row_diagnosis = observation_value.get('@code', None)
                                        row_diagnosis_name = unescape(observation_value.get('@displayName', None))
                                        break
                        observation_effective_times = observation.get('effectiveTime', None)
                        if isinstance(observation_effective_times, dict):
                            observation_effective_time = observation_effective_times.get('@value', None)
                            if isinstance(observation_effective_time, str):
                                row_diagnosis_time = datetime(
                                    int(observation_effective_time[0:4]),
                                    int(observation_effective_time[4:6]),
                                    int(observation_effective_time[6:8])
                                ).date()
                        observation_codes = observation.get('code', None)
                        if observation_codes:
                            if isinstance(observation_codes, dict):
                                observation_codes = [observation_codes]
                            for observation_code in observation_codes:
                                if isinstance(observation_code, dict):
                                    observation_code_code_system = observation_code.get('@codeSystem', '')
                                    if observation_code_code_system == '1.2.643.5.1.13.13.11.1077':
                                        row_diagnosis_kind_code = observation_code.get('@code', None)
                                        row_diagnosis_kind_name = unescape(observation_code.get('@displayName', None))
                                        break
                        if row_diagnosis:
                            diagnoses = diagnoses.union(
                                {
                                    (
                                        row_diagnosis,
                                        row_diagnosis_time,
                                        row_diagnosis_kind_code,
                                        row_diagnosis_name,
                                        row_diagnosis_kind_name
                                    )
                                 }
                            )
                    except:
                        pass

    result = list()
    diagnoses = sorted(
        diagnoses,
        key=lambda x: x[0]+'None'+'999' if x[1] is None and x[2] is None
        else x[0]+x[1].strftime("%Y%m%d")+'999' if x[1] is not None and x[2] is None
        else x[0]+'None'+x[2].zfill(3) if x[1] is None and x[2] is not None
        else x[0]+x[1].strftime("%Y%m%d")+x[2].zfill(3)
    )
    previous_code = None
    for code, dat, kind, name, kind_name in diagnoses:
        if previous_code is None or previous_code != code:
            previous_code = code
            result.append(OrderedDict([
                ('diagnosis_code', code),
                ('diagnosis_name', name),
                ('diagnosis_first_date', dat),
                ('diagnosis_first_kind_code', kind),
                ('diagnosis_first_kind_name', kind_name),
            ]))

    result = \
        sorted(result, key=lambda x: date.today() if x['diagnosis_first_date'] is None else x['diagnosis_first_date'])

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


class GetPatientDiagnosesService:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> PatientListDiagnosisSerializer:
        """
            Retrieve SEMD diagnoses of patient
        """

        # Check input data
        rid = kwargs.get("pk", None)
        if not rid:
            raise ParseError(f"Request must have 'rid' parameter", code='rid')

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
                    regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:*[x:observation[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]]]', payload::xml, '{{x,urn:hl7-org:v3}}'), '<new/>'), '\n', ' ', 'g') as diagnoses,
                    internal_message_id,
                    document_type,
                    array_to_string(xpath('/x:ClinicalDocument/x:effectiveTime/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as date_time
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
                xmls = message_diagnosis[0].split('<new/>')
                internal_message_id = message_diagnosis[1]
                document_type = message_diagnosis[2]
                internal_message_time = datetime(
                    int(message_diagnosis[3][0:4]),
                    int(message_diagnosis[3][4:6]),
                    int(message_diagnosis[3][6:8])
                ).date()
                for xml in xmls:
                    if not xml:
                        continue
                    try:
                        parent = xmltodict.parse(xml)
                        if not isinstance(parent, dict):
                            continue
                        for parent_key, parent_dict in parent.items():
                            if not isinstance(parent_dict, dict):
                                continue
                            parent_node_name = parent_key
                            parent_node_class_code = parent_dict.get('@classCode', None)
                            parent_node_code = None
                            parent_node_display_name = None
                            parent_node_code_system = None
                            parent_node_code_system_version = None
                            parent_node_code_system_name = None
                            parent_node_code_node = parent_dict.get('code', None)
                            if parent_node_code_node and isinstance(parent_node_code_node, dict):
                                parent_node_code = parent_node_code_node.get('@code', None)
                                parent_node_display_name = unescape(parent_node_code_node.get('@displayName', None))
                                parent_node_code_system = parent_node_code_node.get('@codeSystem', None)
                                parent_node_code_system_version = parent_node_code_node.get('@codeSystemVersion', None)
                                parent_node_code_system_name = unescape(parent_node_code_node.get('@codeSystemName', None))
                            for key, entry_list in parent_dict.items():
                                if not isinstance(entry_list, list):
                                    entry_list = [entry_list]
                                for entry in entry_list:
                                    if not isinstance(entry, dict):
                                        continue
                                    observation = entry.get('observation', None)
                                    if not observation:
                                        continue

                                    row_date = None
                                    observation_effective_times = observation.get('effectiveTime', None)
                                    if isinstance(observation_effective_times, dict):
                                        observation_effective_time = observation_effective_times.get('@value', None)
                                        if isinstance(observation_effective_time, str):
                                            row_date = datetime(
                                                int(observation_effective_time[0:4]),
                                                int(observation_effective_time[4:6]),
                                                int(observation_effective_time[6:8])
                                            ).date()

                                    node_code = None
                                    node_display_name = None
                                    node_code_system = None
                                    node_code_system_version = None
                                    node_code_system_name = None
                                    node_code_node = observation.get('code', None)
                                    if node_code_node and isinstance(node_code_node, dict):
                                        node_code = node_code_node.get('@code', None)
                                        node_display_name = unescape(node_code_node.get('@displayName', None))
                                        node_code_system = node_code_node.get('@codeSystem', None)
                                        node_code_system_version = node_code_node.get('@codeSystemVersion', None)
                                        node_code_system_name = unescape(node_code_node.get('@codeSystemName', None))

                                    row_diagnosis = None
                                    row_diagnosis_name = None
                                    observation_values = observation.get('value', None)
                                    if observation_values:
                                        if not isinstance(observation_values, list):
                                            observation_values = [observation_values]
                                        for observation_value in observation_values:
                                            if not isinstance(observation_value, dict):
                                                continue
                                            observation_value_code_system = observation_value.get('@codeSystem', '')
                                            if observation_value_code_system == '1.2.643.5.1.13.13.11.1005':
                                                row_diagnosis = observation_value.get('@code', None)
                                                row_diagnosis_name = unescape(observation_value.get('@displayName', None))
                                                break

                                    if row_diagnosis:
                                        diagnoses = diagnoses.union(
                                            {
                                                (
                                                    row_diagnosis,
                                                    row_date,
                                                    node_code,
                                                    row_diagnosis_name,
                                                    internal_message_id,
                                                    document_type,
                                                    internal_message_time,
                                                    parent_node_name,
                                                    parent_node_class_code,
                                                    parent_node_code,
                                                    parent_node_display_name,
                                                    parent_node_code_system,
                                                    parent_node_code_system_version,
                                                    parent_node_code_system_name,
                                                    node_display_name,
                                                    node_code_system,
                                                    node_code_system_version,
                                                    node_code_system_name
                                                )
                                            }
                                        )
                    except:
                        pass

        diagnoses = sorted(
            diagnoses,
            key=lambda x: x[0]+'None'+'999' if x[1] is None and x[2] is None
            else x[0]+x[1].strftime("%Y%m%d")+'999' if x[1] is not None and x[2] is None
            else x[0]+'None'+x[2].zfill(3) if x[1] is None and x[2] is not None
            else x[0]+x[1].strftime("%Y%m%d")+x[2].zfill(3)
        )
        result_diagnoses = list()
        result_diagnoses_in_semds = list()
        diagnosis_code = None
        diagnosis_name = None
        diagnosis_first_date = None
        diagnosis_first_kind_code = None
        diagnosis_first_kind_name = None
        previous_code = None
        for row_diagnosis, row_date, node_code, row_diagnosis_name, internal_message_id, document_type, \
                internal_message_time, parent_node_name, parent_node_class_code, parent_node_code, \
                parent_node_display_name, parent_node_code_system, parent_node_code_system_version, \
                parent_node_code_system_name, node_display_name, node_code_system, \
                node_code_system_version, node_code_system_name in diagnoses:
            if previous_code is None or previous_code != row_diagnosis:
                if previous_code is not None:
                    result_diagnoses.append(OrderedDict([
                        ('diagnosis_code', diagnosis_code),
                        ('diagnosis_name', diagnosis_name),
                        ('diagnosis_first_date', diagnosis_first_date),
                        ('diagnosis_first_kind_code', diagnosis_first_kind_code),
                        ('diagnosis_first_kind_name', diagnosis_first_kind_name),
                        ('diagnoses_in_semds', result_diagnoses_in_semds),
                    ]))
                previous_code = row_diagnosis
                diagnosis_code = row_diagnosis
                diagnosis_name = row_diagnosis_name
                diagnosis_first_date = row_date
                diagnosis_first_kind_code = node_code
                diagnosis_first_kind_name = node_display_name
                result_diagnoses_in_semds = list()

            result_diagnoses_in_semds.append(OrderedDict([
                ('date', row_date),
                ('document_type', document_type),
                ('internal_message_id', internal_message_id),
                ('internal_message_time', internal_message_time),
                ('parent_node_name', parent_node_name),
                ('parent_node_class_code', parent_node_class_code),
                ('parent_node_code_node', OrderedDict([
                    ('code', parent_node_code),
                    ('display_name', parent_node_display_name),
                    ('code_system', parent_node_code_system),
                    ('code_system_version', parent_node_code_system_version),
                    ('code_system_name', parent_node_code_system_name),
                ])),
                ('code_node', OrderedDict([
                    ('code', node_code),
                    ('display_name', node_display_name),
                    ('code_system', node_code_system),
                    ('code_system_version', node_code_system_version),
                    ('code_system_name', node_code_system_name),
                ])),
            ]))

        if previous_code is not None:
            result_diagnoses.append(OrderedDict([
                ('diagnosis_code', diagnosis_code),
                ('diagnosis_name', diagnosis_name),
                ('diagnosis_first_date', diagnosis_first_date),
                ('diagnosis_first_kind_code', diagnosis_first_kind_code),
                ('diagnosis_first_kind_name', diagnosis_first_kind_name),
                ('diagnoses_in_semds', result_diagnoses_in_semds),
            ]))

        result_diagnoses = \
            sorted(
                result_diagnoses,
                key=lambda x: date.today() if x['diagnosis_first_date'] is None else x['diagnosis_first_date']
            )

        patient_diagnosis_list_serializer = PatientDiagnosisSerializer(result_diagnoses, many=True)

        count = len(result_diagnoses)
        items_per_page = count
        start_item_index = 0 if count == 0 else 1
        end_item_index = count
        previous_page = None
        current_page = 1
        next_page = None

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
        return_serializer = PatientListDiagnosisSerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok' if count > 0 else 'Result set is empty',
                'result': patient_diagnosis_list_serializer.data,
                'retExtInfo': pagination_list_serializer.data,
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer
