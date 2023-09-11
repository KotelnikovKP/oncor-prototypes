from datetime import datetime, timezone

import xmltodict
from django.db import transaction, connections

from api.models.orientdb_engine import orient_db_client
from api.models.semd_models import SemdDiagnosis, SemdService
from backend.settings import SERVICE_BY_POST


def run(*args):
    print("-----------------------------------------------------------------------")
    print("Procedure FILL CUBES was stated!")
    if 'erase-cubes' in args:
        print("Found 'erase-cubes' parameter, it is starting delete cubes records...")
        with transaction.atomic():
            semd_diagnoses = SemdDiagnosis.objects.all()
            semd_diagnoses.delete()
        print("    Patient-SEMD-diagnosis cube has been cleaned")
        with transaction.atomic():
            semd_services = SemdService.objects.all()
            semd_services.delete()
        print("    Patient-SEMD-service cube has been cleaned")

    # Define queries
    query_body = """
        SELECT 
            @rid, 
            person.code as code, 
            observer.nsiMedOrg.oid as mo_oid,
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

    # Calculate count of queryset
    orient_result = orient_db_client.query(query_count_body, -1)
    count = orient_result[0].count
    print(f'Found {count} patients.')

    # Get queryset
    patients = orient_db_client.query(query_body, -1)

    i = n = 0
    # Get SEMD records for each patient in queryset
    for patient in patients:
        # Get patient parameters
        ptn_id = str(patient.oRecordData.get('rid', None))
        ptn_code = patient.oRecordData.get('code', None)
        ptn_mo_oid = patient.oRecordData.get('mo_oid', None)
        ptn_tags = [] \
            if patient.oRecordData.get('tags', None) is None \
            else [str(rid) for rid in patient.oRecordData.get('tags', None)]
        i += 1
        print(f"{str(i).zfill(6)} {ptn_id}: ", end='')

        if not ptn_id:
            continue

        # Define records queries
        query_body = f"""
            SELECT 
                @rid, 
                internalMessageId 
            FROM 
                (
                    SELECT 
                        EXPAND(records) 
                    FROM 
                        ptn 
                    WHERE 
                        @rid={ptn_id}
                ) 
            WHERE 
                @class="RcSMS"
        """

        # Get records
        records = orient_db_client.query(query_body, -1)
        records_count = len(records)
        print(f"{records_count} SEMDs")
        n += records_count

        if not records_count:
            continue

        rc_ids = {
            record.oRecordData.get('internalMessageId', None): record.oRecordData.get('rid', None)
            for record in records 
            if record.oRecordData.get('internalMessageId', None)
        }
        messages = [
            "'" + record.oRecordData.get('internalMessageId', None) + "'" 
            for record in records
            if record.oRecordData.get('internalMessageId', None)
        ]
        query_body = """
            SELECT
                internal_message_id,
                date_time as time_rc,
                document_type,
                array_to_string(xpath('/x:ClinicalDocument/x:code[@codeSystem="1.2.643.5.1.13.13.99.2.592"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as nsi_doc_type_592,
                array_to_string(xpath('/x:ClinicalDocument/x:code[@codeSystem="1.2.643.5.1.13.13.11.1522"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ',') as nsi_doc_type_1522,
                sms_profile as profile,
                array_to_string(xpath('/x:ClinicalDocument/x:author/x:assignedAuthor/x:representedOrganization/x:id/@root', payload::xml, '{{x,urn:hl7-org:v3}}'), ' ') as author_mo_oid,
                array_to_string(xpath('/x:ClinicalDocument/x:author/x:assignedAuthor/x:id[@root="1.2.643.100.3"]/@extension', payload::xml, '{{x,urn:hl7-org:v3}}'), ' ') as author_snils,
                array_to_string(xpath('/x:ClinicalDocument/x:author/x:assignedAuthor/x:code[@codeSystem="1.2.643.5.1.13.13.11.1002"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ' ') as author_post,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:*[x:observation[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]]]', payload::xml, '{{x,urn:hl7-org:v3}}'), '<new/>'), '\n', ' ', 'g') as diagnoses,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]]', payload::xml, '{{x,urn:hl7-org:v3}}'), '<new/>'), '\n', ' ', 'g') as services,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:*[@codeSystem="1.2.643.5.1.13.13.11.1471"]]', payload::xml, '{{x,urn:hl7-org:v3}}'), '<new/>'), '\n', ' ', 'g') as instrumental_diagnostics
            FROM
                vimis_sending
            WHERE
                internal_message_id in (""" + ','.join(messages) + ')'
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            semds = cursor.fetchall()

        if not semds:
            continue

        # Start transaction for each patient
        with transaction.atomic():
            # Get diagnoses for each SEMD
            for semd in semds:
                internal_message_id = semd[0]
                rc_id = rc_ids[internal_message_id]
                time_rc = datetime(semd[1].year, semd[1].month, semd[1].day,
                                   semd[1].hour, semd[1].minute, semd[1].second, tzinfo=timezone.utc)
                document_type = semd[2]
                nsi_doc_type = semd[3] if semd[3] else semd[4]
                profile = semd[5]
                author_mo_oid = semd[6]
                author_snils = semd[7]
                author_post = semd[8]
                xml_diagnoses = semd[9].split('<new/>')
                xml_services = semd[10].split('<new/>')
                xml_instrumental_diagnostics = semd[11].split('<new/>')

                # Calculate diagnoses set
                diagnoses = set()
                for xml in xml_diagnoses:
                    if not xml:
                        continue
                    try:
                        row_diagnosis_code1379 = None
                        parent = xmltodict.parse(xml)
                        if not isinstance(parent, dict):
                            continue
                        for parent_key, parent_dict in parent.items():
                            if not isinstance(parent_dict, dict):
                                continue
                            row_diagnosis_code1076 = None
                            parent_node_code_node = parent_dict.get('code', None)
                            if parent_node_code_node and isinstance(parent_node_code_node, dict) and \
                                    parent_node_code_node.get('@codeSystem', None) == '1.2.643.5.1.13.13.11.1076':
                                row_diagnosis_code1076 = parent_node_code_node.get('@code', None)

                            for key, entry_list in parent_dict.items():
                                if not isinstance(entry_list, list):
                                    entry_list = [entry_list]

                                for entry in entry_list:
                                    if not isinstance(entry, dict):
                                        continue
                                    observation = entry.get('observation', None)
                                    if not observation:
                                        continue

                                    row_diagnosis_date = None
                                    observation_effective_times = observation.get('effectiveTime', None)
                                    if isinstance(observation_effective_times, dict):
                                        observation_effective_time = observation_effective_times.get('@value', None)
                                        if isinstance(observation_effective_time, str):
                                            row_diagnosis_date = datetime(
                                                int(observation_effective_time[0:4]),
                                                int(observation_effective_time[4:6]),
                                                int(observation_effective_time[6:8]),
                                                tzinfo=timezone.utc
                                            ).date()

                                    row_diagnosis_code1077 = None
                                    node_code_node = observation.get('code', None)
                                    if node_code_node and isinstance(node_code_node, dict) and \
                                            node_code_node.get('@codeSystem', None) == '1.2.643.5.1.13.13.11.1077':
                                        row_diagnosis_code1077 = node_code_node.get('@code', None)

                                    row_diagnosis_mkb10 = None
                                    observation_values = observation.get('value', None)
                                    if observation_values:
                                        if not isinstance(observation_values, list):
                                            observation_values = [observation_values]

                                        for observation_value in observation_values:
                                            if not isinstance(observation_value, dict):
                                                continue
                                            observation_value_code_system = observation_value.get('@codeSystem', '')
                                            if observation_value_code_system == '1.2.643.5.1.13.13.11.1005':
                                                row_diagnosis_mkb10 = observation_value.get('@code', None)
                                                break

                                    if row_diagnosis_mkb10:
                                        diagnoses = diagnoses.union(
                                            {
                                                (
                                                    row_diagnosis_mkb10,
                                                    row_diagnosis_date,
                                                    row_diagnosis_code1379,
                                                    row_diagnosis_code1076,
                                                    row_diagnosis_code1077
                                                )
                                            }
                                        )
                    except:
                        pass

                # Calculate services set
                services = set()
                for xml in xml_services:
                    if not xml:
                        continue
                    try:
                        row_instrumental_diagnostics_code = None
                        parent = xmltodict.parse(xml)
                        if not isinstance(parent, dict):
                            continue
                        for parent_key, parent_dict in parent.items():
                            if not isinstance(parent_dict, dict):
                                continue

                            row_service_date = None
                            effective_times = parent_dict.get('effectiveTime', None)
                            if isinstance(effective_times, dict):
                                effective_time = effective_times.get('@value', None)
                                if isinstance(effective_time, str):
                                    row_service_date = datetime(
                                        int(effective_time[0:4]),
                                        int(effective_time[4:6]),
                                        int(effective_time[6:8]),
                                        tzinfo=timezone.utc
                                    ).date()
                                else:
                                    low_effective_times = effective_times.get('low', None)
                                    if isinstance(low_effective_times, dict):
                                        effective_time = low_effective_times.get('@value', None)
                                        if isinstance(effective_time, str):
                                            row_service_date = datetime(
                                                int(effective_time[0:4]),
                                                int(effective_time[4:6]),
                                                int(effective_time[6:8]),
                                                tzinfo=timezone.utc
                                            ).date()

                            row_service_code = None
                            for key, value in parent_dict.items():
                                if not isinstance(value, dict):
                                    continue
                                code_system = value.get('@codeSystem', '')
                                if code_system == '1.2.643.5.1.13.13.11.1070':
                                    row_service_code = value.get('@code', None)
                                    break

                            if row_service_code:
                                if not row_service_date and document_type == '5':
                                    row_service_date = datetime(time_rc.year, time_rc.month, time_rc.day,
                                                                tzinfo=timezone.utc).date()
                                services = services.union(
                                    {
                                        (
                                            row_service_code,
                                            row_service_date,
                                            row_instrumental_diagnostics_code
                                        )
                                    }
                                )
                    except:
                        pass

                # Calculate instrumental_diagnostics set if services set is empty
                if not services:
                    instrumental_diagnostics = set()
                    for xml in xml_instrumental_diagnostics:
                        if not xml:
                            continue
                        try:
                            parent = xmltodict.parse(xml)
                            if not isinstance(parent, dict):
                                continue
                            for parent_key, parent_dict in parent.items():

                                row_instrumental_diagnostics_date = None
                                effective_times = parent_dict.get('effectiveTime', None)
                                if isinstance(effective_times, dict):
                                    effective_time = effective_times.get('@value', None)
                                    if isinstance(effective_time, str):
                                        row_instrumental_diagnostics_date = datetime(
                                            int(effective_time[0:4]),
                                            int(effective_time[4:6]),
                                            int(effective_time[6:8]),
                                            tzinfo=timezone.utc
                                        ).date()
                                    else:
                                        low_effective_times = effective_times.get('low', None)
                                        if isinstance(low_effective_times, dict):
                                            effective_time = low_effective_times.get('@value', None)
                                            if isinstance(effective_time, str):
                                                row_instrumental_diagnostics_date = datetime(
                                                    int(effective_time[0:4]),
                                                    int(effective_time[4:6]),
                                                    int(effective_time[6:8]),
                                                    tzinfo=timezone.utc
                                                ).date()

                                row_instrumental_diagnostics_code = None
                                for key, value in parent_dict.items():
                                    if not isinstance(value, dict):
                                        continue
                                    code_system = value.get('@codeSystem', '')
                                    if code_system == '1.2.643.5.1.13.13.11.1471':
                                        row_instrumental_diagnostics_code = value.get('@code', None)
                                        break

                                if row_instrumental_diagnostics_code:
                                    if not row_instrumental_diagnostics_date and document_type == '5':
                                        row_instrumental_diagnostics_date = datetime(time_rc.year, time_rc.month,
                                                                                     time_rc.day,
                                                                                     tzinfo=timezone.utc).date()
                                    instrumental_diagnostics = instrumental_diagnostics.union(
                                        {
                                            (
                                                row_instrumental_diagnostics_code,
                                                row_instrumental_diagnostics_date
                                            )
                                        }
                                    )
                        except:
                            pass

                    for instrumental_diagnostic in instrumental_diagnostics:
                        query_body = """
                            SELECT
                                json->>'NMU' as services
                            FROM
                                directory
                            WHERE
                                passport_oid='1.2.643.5.1.13.13.11.1471' AND
                                id='""" + instrumental_diagnostic[0] + "'"
                        with connections['rosminzdrav-directories'].cursor() as cursor:
                            cursor.execute(query_body)
                            ins_diag_services = cursor.fetchall()
                        if len(ins_diag_services) == 1:
                            ins_diag_services = ins_diag_services[0][0]
                            if ins_diag_services:
                                ins_diag_services = ins_diag_services.split('; ')
                                for ins_diag_service in ins_diag_services:
                                    services = services.union(
                                        {
                                            (
                                                ins_diag_service,
                                                instrumental_diagnostic[1],
                                                instrumental_diagnostic[0]
                                            )
                                        }
                                    )

                    if not services and document_type == '20':
                        row_service_code = SERVICE_BY_POST.get(author_post, None)
                        if row_service_code:
                            services = services.union(
                                {
                                    (
                                        row_service_code,
                                        datetime(time_rc.year, time_rc.month, time_rc.day,
                                                 tzinfo=timezone.utc).date(),
                                        None
                                    )
                                }
                            )

                # Save records to cubes
                for diagnosis in diagnoses:
                    semd_diagnosis = SemdDiagnosis()
                    semd_diagnosis.ptn_id = ptn_id
                    semd_diagnosis.ptn_code = ptn_code
                    semd_diagnosis.ptn_mo_oid = ptn_mo_oid
                    semd_diagnosis.ptn_tags = ptn_tags
                    semd_diagnosis.rc_id = rc_id
                    semd_diagnosis.time_rc = time_rc
                    semd_diagnosis.document_type = document_type
                    semd_diagnosis.nsi_doc_type = nsi_doc_type
                    semd_diagnosis.profile = profile
                    semd_diagnosis.author_mo_oid = author_mo_oid
                    semd_diagnosis.author_snils = author_snils
                    semd_diagnosis.author_post = author_post
                    semd_diagnosis.internal_message_id = internal_message_id
                    semd_diagnosis.diagnosis_mkb10 = diagnosis[0]
                    semd_diagnosis.diagnosis_date = diagnosis[1]
                    semd_diagnosis.diagnosis_code1379 = diagnosis[2]
                    semd_diagnosis.diagnosis_code1076 = diagnosis[3]
                    semd_diagnosis.diagnosis_code1077 = diagnosis[4]
                    semd_diagnosis.save()

                for service in services:
                    semd_service = SemdService()
                    semd_service.ptn_id = ptn_id
                    semd_service.ptn_code = ptn_code
                    semd_diagnosis.ptn_mo_oid = ptn_mo_oid
                    semd_service.ptn_tags = ptn_tags
                    semd_service.rc_id = rc_id
                    semd_service.time_rc = time_rc
                    semd_service.document_type = document_type
                    semd_service.nsi_doc_type = nsi_doc_type
                    semd_service.profile = profile
                    semd_service.author_mo_oid = author_mo_oid
                    semd_service.author_snils = author_snils
                    semd_service.author_post = author_post
                    semd_service.internal_message_id = internal_message_id
                    semd_service.service_code = service[0]
                    semd_service.service_date = service[1]
                    semd_service.instrumental_diagnostics_code = service[2]
                    semd_service.save()

    print(f"SEMDs count = {n}")
