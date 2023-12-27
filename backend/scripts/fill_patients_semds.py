import math
from datetime import datetime, timezone
from typing import Optional

import xmltodict
from django.db import transaction, connections, connection

from api.models.oncor_data_analytics_models import RcSms
from api.models.semd_models import PatientDiagnosis, PatientSEMD

ITEMS_IN_ITERATION = 1000
INDICATOR_MIN_LENGTH = 5
EXPECTED_INDICATORS = {
    '1': {
        'recipient': 'МО напр.',
        'purpose': 'цель напр.',
        'service': 'услуга напр.'
    },
    '2': {
        'protocol': 'протокол',
        'conclusion': 'заключение',
        'recommendation': 'рекомендации',
    },
    '3': {
        'laboratory_tests': 'лаб. иссл.',
    },
    '4': {
        'histological_tests': 'гист. иссл.',
    },
    '5': {
        'protocol': 'протокол',
        'conclusion': 'заключение',
        'recommendation': 'рекомендации',
    },
    '6': {
        'date': 'дата консилиума',
        'number': 'номер протокола',
        'purpose': 'цель консилиума',
        'form': 'форма проведения',
        'conclusion': 'решение консилиума',
        'diagnostics': 'инстр. иссл.',
        'laboratory_tests': 'лаб. иссл.',
        'treatments': 'лечение'
    },
    '8': {
        'date_start': 'дата начала госп.',
        'urgency': 'срочность госп.',
        'stateadm': 'состояние при поступлении',
        'date_end': 'дата окончания госп.',
        'statedis': 'состояние при выписке',
        'result': 'результат госп.',
        'consultations': 'консультации',
        'diagnostics': 'инстр. иссл.',
        'laboratory_tests': 'лаб. иссл.',
        'morphology_tests': 'морф. иссл.',
        'sum_drug': 'медикаментозное лечение',
        'ray_therapy': 'лучевая терапия',
        'chemo_therapy': 'химиотерапия',
        'hormone_therapy': 'гормонотерапия',
        'sur': 'операции'
    },
    '9': {
        'cytological_tests': 'цит. иссл.',
    },
    '10': {
        'sur': 'операция',
        'date_start': 'дата-время начала операции'
    },
    '11': {
        'late_reason': 'причины поздней диагностики',
        'tnm': 'TNM',
        'stage': 'стадия',
        'side': 'сторона поражения',
        'morph_class': 'морф. тип',
        'clinical_group': 'клин. группа',
        'how_discover': 'обст. выявления',
        'topograph': 'топография',
        'loc_far_met': 'локализация',
        'tumor_number': 'номер опухоли',
        'tumor_main': 'признак основной опухоли',
        'plural': 'вид первично-множественной опухоли',
        'method': 'метод подтверждения',
    },
    '12': {
        'date_start': 'дата начала лечения',
        'date_end': 'дата окончания лечения',
        'order': 'порядок обращения',
        'result': 'результат',
        'consultations': 'консультации',
        'diagnostics': 'инстр. иссл.',
        'laboratory_tests': 'лаб. иссл.',
        'morphology_tests': 'морф. иссл.',
        'sum_drug': 'медикаментозное лечение',
        'sur': 'операции'
    },
    '20': {
        'protocol': 'протокол',
        'conclusion': 'заключение',
        'recommendation': 'рекомендации',
    },
    '27': {
        'recipient': 'МО напр.',
        'service': 'услуга напр.'
    },
    '37': {
        'recipient': 'МО напр.',
        'tnm': 'TNM',
        'stage': 'стадия',
        'side': 'сторона поражения',
        'morph_class': 'морф. тип',
        'clinical_group': 'клин. группа',
        'how_discover': 'обст. выявления',
        'topograph': 'топография',
        'loc_far_met': 'локализация',
        'tumor_number': 'номер опухоли',
        'tumor_main': 'признак основной опухоли',
        'plural': 'вид первично-множественной опухоли',
        'method': 'метод подтверждения',
    },
}
CANCER_DIAGNOSES = [
    ('C00', 'C97'),
    ('D00', 'D09'),
    ('D21', ),
    ('D31', 'D33'),
    ('D35', 'D48')
]
PRECANCER_DIAGNOSES = [
    'B18.0', 'B18.1', 'B18.2',
    'B20.0', 'B20.1', 'B20.2', 'B20.3', 'B20.4', 'B20.5', 'B20.6', 'B20.7', 'B20.8', 'B20.9',
    'B21.0', 'B21.1', 'B21.2', 'B21.3', 'B21.7', 'B21.8', 'B21.9',
    'B22.0', 'B22.1', 'B22.2', 'B22.7',
    'B23.0', 'B23.1', 'B23.2', 'B23.8',
    ('B24', ),
    'D10.0', 'D10.1', 'D10.2', 'D10.3', 'D10.4', 'D10.5', 'D10.6', 'D10.7', 'D10.9',
    'D11.0', 'D11.7', 'D11.9',
    'D12.6', 'D12.8',
    'D13.1', 'D13.4', 'D13.7',
    'D14.0', 'D14.1', 'D14.2', 'D14.3', 'D14.4',
    'D16.0', 'D16.1', 'D16.2', 'D16.3', 'D16.4', 'D16.5', 'D16.6', 'D16.7', 'D16.8', 'D16.9',
    'D22.0', 'D22.1', 'D22.2', 'D22.3', 'D22.4', 'D22.5', 'D22.6', 'D22.7', 'D22.9',
    'D23.0', 'D23.1', 'D23.2', 'D23.3', 'D23.4', 'D23.5', 'D23.6', 'D23.7', 'D23.9',
    ('D24', ),
    'D29.1',
    'D30.0', 'D30.3', 'D30.4',
    'D81.0', 'D81.1', 'D81.2', 'D81.3', 'D81.4', 'D81.5', 'D81.6', 'D81.7', 'D81.8', 'D81.9',
    'D82.0', 'D82.1', 'D82.2', 'D82.3', 'D82.4', 'D82.8', 'D82.9',
    'D83.0', 'D83.1', 'D83.2', 'D83.8', 'D83.9',
    'D84.0', 'D84.1', 'D84.8', 'D84.9',
    'E04.1', 'E04.2',
    'E05.0', 'E05.1', 'E05.2',
    'E06.3',
    'E21.0',
    'E22.0',
    'E28.2',
    'E34.5', 'E34.8',
    'J31.0', 'J31.1', 'J31.2',
    'J33.0', 'J33.1', 'J33.8', 'J33.9',
    'J37.0', 'J37.1',
    'J38.1', 'J38.3',
    'K13.0', 'K13.2', 'K13.7',
    'K21.0',
    'K22.0', 'K22.1', 'K22.2', 'K22.7',
    'K25.0', 'K25.1', 'K25.2', 'K25.3', 'K25.4', 'K25.5', 'K25.6', 'K25.7', 'K25.9',
    'K29.4', 'K29.5',
    'K31.7',
    'K50.0', 'K50.1', 'K50.8', 'K50.9',
    'K51.0', 'K51.1', 'K51.2', 'K51.3', 'K51.4', 'K51.5', 'K51.8', 'K51.9',
    'K62.1',
    'K74.3', 'K74.4', 'K74.5', 'K74.6',
    'L43.0', 'L43.1', 'L43.3', 'L43.8', 'L43.9',
    'L57.0', 'L57.1', 'L57.2', 'L57.3', 'L57.4', 'L57.5', 'L57.8', 'L57.9',
    ('L82', ),
    'L85.8',
    'L93.0', 'L93.1', 'L93.2',
    'M85.0', 'M85.1', 'M85.2', 'M85.3', 'M85.4', 'M85.5', 'M85.6', 'M85.8', 'M85.9',
    'M88.0', 'M88.8', 'M88.9',
    'M96.0', 'M96.1', 'M96.2', 'M96.3', 'M96.4', 'M96.5', 'M96.6', 'M96.8', 'M96.9',
    'N48.0',
    'N60.0', 'N60.1', 'N60.2', 'N60.3', 'N60.4', 'N60.8', 'N60.9',
    'N84.0', 'N84.1', 'N84.2', 'N84.3', 'N84.8', 'N84.9',
    'N85.0', 'N85.1',
    'N87.0', 'N87.1', 'N87.2', 'N87.9',
    'N88.0', 'N89.2', 'N90.2',
    'Q50.0', 'Q50.1', 'Q50.2', 'Q50.3', 'Q50.4', 'Q50.5', 'Q50.6',
    'Q56.0', 'Q56.1', 'Q56.2', 'Q56.3', 'Q56.4',
    'Q78.1', 'Q78.4',
    'Q82.1', 'Q82.5',
    'Q85.1',
    'Q96.0', 'Q96.1', 'Q96.2', 'Q96.3', 'Q96.4', 'Q96.8', 'Q96.9',
    'Q97.0', 'Q97.1', 'Q97.2', 'Q97.3', 'Q97.8', 'Q97.9',
    'Q98.0', 'Q98.1', 'Q98.2', 'Q98.3', 'Q98.4', 'Q98.5', 'Q98.6', 'Q98.7', 'Q98.8', 'Q98.9',
    'Q99.0', 'Q99.1', 'Q99.2', 'Q99.8', 'Q99.9'
]


def run(*args):
    print("-----------------------------------------------------------------------")
    print(f"Procedure FILL PATIENTS SEMDs was stated!")
    if 'erase-semds' in args:
        print("Found 'erase-semds' parameter, it is starting delete records...")
        with transaction.atomic():
            patient_semds = PatientSEMD.objects.all()
            patient_semds.delete()
        print("    Patient SEMDs were cleaned")

    # Get queryset
    sms_records = (
        RcSms.objects
        .using('oncor-data-analytics')
        .filter(time_rc__gte=datetime(datetime.now().year, 1, 1), profile='ONCO')   # , soap_doc_type='7'
    )
    count = sms_records.count()
    print(f'Found {count} sms.')

    i = n = 0
    # Get records for each sms in queryset
    for k in range(math.ceil(count / ITEMS_IN_ITERATION)):
        sms_records = (
            RcSms.objects
            .using('oncor-data-analytics')
            .filter(time_rc__gte=datetime(datetime.now().year, 1, 1), profile='ONCO')   # , soap_doc_type='7'
            .order_by('id')[k * ITEMS_IN_ITERATION:(k + 1) * ITEMS_IN_ITERATION]
        )
        with transaction.atomic():
            for sms in sms_records:
                i += 1
                print(f"{str(i).zfill(7)} from {count}: {sms.id}, {sms.rc_id}")

                ptn_id = sms.ptn_id
                rc_id = sms.rc_id
                ptn_code = sms.ptn_code
                ehr_id = sms.ehr_id
                rc_time = datetime(sms.time_rc.year, sms.time_rc.month, sms.time_rc.day, sms.time_rc.hour,
                                   sms.time_rc.minute, sms.time_rc.second, tzinfo=timezone.utc)
                cda_sent_local_date = sms.cda_sent_local_date
                if cda_sent_local_date is None:
                    cda_sent_local_date = rc_time.date()
                internal_message_id = sms.internal_message_id
                profile = sms.profile
                soap_doc_type = sms.soap_doc_type
                sms_summary = sms.sms_summary or dict()
                author_mo_oid = sms_summary.get('author_mo_oid', None)
                author_mo_dpt_oid = sms_summary.get('author_mo_dpt_oid', None)
                author_snils = sms_summary.get('author_snils', None)
                author_post = sms_summary.get('author_post', None)
                diagnoses = sms_summary.get('diagnoses', list())
                services = sms_summary.get('services', list())
                cda_time = sms_summary.get('date_cda', None)
                if cda_time is not None:
                    if len(cda_time) == 8:
                        cda_time = datetime(int(cda_time[0:4]), int(cda_time[4:6]), int(cda_time[6:8]),
                                            tzinfo=timezone.utc)
                    else:
                        cda_time = datetime(int(cda_time[0:4]), int(cda_time[4:6]), int(cda_time[6:8]),
                                            int(cda_time[8:10]), int(cda_time[10:12]), tzinfo=timezone.utc)
                sms_type = sms_summary.get('type', None)

                if soap_doc_type == '37' and sms_summary.get('ds_code', None):
                    d = {
                        'mkb10': sms_summary.get('ds_code', None),
                        'code1077': '1',
                        'code197': 'DGN'
                    }
                    dt = sms_summary.get('ds_date', None)
                    if dt:
                        dt = dt[0:4] + '-' + dt[4:6] + '-' + dt[6:8]
                        d['date'] = dt
                    code1076 = sms_summary.get('ds_prove', None)
                    if code1076:
                        d['code1076'] = code1076
                    diagnoses.append(d)

                if len(diagnoses) == 0:
                    diagnoses = get_diagnoses(internal_message_id)

                is_cancer_diagnoses, is_precancer_diagnoses = check_diagnoses(diagnoses)

                diagnosis = None
                diagnosis_mkb10 = None
                diagnosis_date = None
                diagnosis_code197 = None
                diagnosis_code1076 = None
                diagnosis_code1077 = None
                is_cancer_diagnosis = is_precancer_diagnosis = False

                patient_diagnosis = None
                patient_diagnoses = PatientDiagnosis.objects.filter(ptn_id=ptn_id).order_by('-diagnosis_date')

                for pd in patient_diagnoses:
                    if pd.diagnosis_date and pd.diagnosis_date <= cda_sent_local_date:
                        patient_diagnosis = pd
                        break

                if not patient_diagnosis and len(patient_diagnoses):
                    patient_diagnosis = patient_diagnoses[0]

                if patient_diagnosis:
                    is_in_cancer_register = True
                    mkb10 = patient_diagnosis.diagnosis_mkb10.split('.')
                    if len(mkb10) > 1:
                        rc_diagnosis_mkb10 = mkb10[0] + '.' + str(int(mkb10[1]))
                    else:
                        rc_diagnosis_mkb10 = mkb10[0]
                    rc_diagnosis_mkb10_l1 = mkb10[0]
                    rc_diagnosis_date = patient_diagnosis.diagnosis_date

                    same_diagnoses = list()
                    similar_diagnoses = list()
                    for d in diagnoses:
                        if d.get('mkb10', None) == rc_diagnosis_mkb10:
                            same_diagnoses.append(d)
                        if d.get('mkb10', '').split('.')[0] == rc_diagnosis_mkb10_l1:
                            similar_diagnoses.append(d)

                    if same_diagnoses:
                        diagnosis = get_diagnosis(same_diagnoses, code1077='1', code1076='3', code197='DGN',
                                                  date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(same_diagnoses, code1077='1', code1076='4', code197='DGN',
                                                      date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(same_diagnoses, code1077='1', code1076='3', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(same_diagnoses, code1077='1', code1076='4', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(same_diagnoses, code1077='1', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(same_diagnoses, date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(same_diagnoses)

                    if diagnosis is None and similar_diagnoses:
                        diagnosis = get_diagnosis(similar_diagnoses, code1077='1', code1076='3', code197='DGN',
                                                  date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(similar_diagnoses, code1077='1', code1076='4', code197='DGN',
                                                      date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(similar_diagnoses, code1077='1', code1076='3', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(similar_diagnoses, code1077='1', code1076='4', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(similar_diagnoses, code1077='1', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(similar_diagnoses, date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(similar_diagnoses)

                    if diagnosis is None and diagnoses:
                        diagnosis = get_diagnosis(diagnoses, code1077='1', code1076='3', code197='DGN',
                                                  date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, code1077='1', code1076='4', code197='DGN',
                                                      date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, code1077='1', code1076='3', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, code1077='1', code1076='4', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, code1077='1', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses)

                    if diagnosis:
                        diagnosis_mkb10 = diagnosis.get('mkb10', None)
                        diagnosis_date = diagnosis.get('date', None)
                        diagnosis_code197 = diagnosis.get('code197', None)
                        diagnosis_code1076 = diagnosis.get('code1076', None)
                        diagnosis_code1077 = diagnosis.get('code1077', None)
                        is_cancer_diagnosis, is_precancer_diagnosis = check_diagnosis(diagnosis)

                else:
                    is_in_cancer_register = False
                    rc_diagnosis_mkb10 = None
                    rc_diagnosis_date = None

                    if diagnoses:
                        diagnosis = get_diagnosis(diagnoses, code1077='1', code1076='3', code197='DGN',
                                                  date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, code1077='1', code1076='4', code197='DGN',
                                                      date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, code1077='1', code1076='3', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, code1077='1', code1076='4', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, code1077='1', date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses, date_expected=True)
                        if diagnosis is None:
                            diagnosis = get_diagnosis(diagnoses)

                    if diagnosis:
                        diagnosis_mkb10 = diagnosis.get('mkb10', None)
                        diagnosis_date = diagnosis.get('date', None)
                        diagnosis_code197 = diagnosis.get('code197', None)
                        diagnosis_code1076 = diagnosis.get('code1076', None)
                        diagnosis_code1077 = diagnosis.get('code1077', None)
                        is_cancer_diagnosis, is_precancer_diagnosis = check_diagnosis(diagnosis)

                semd_content, content_error = get_content(internal_message_id, soap_doc_type)

                diagnosis_error = ''
                if not diagnosis_mkb10:
                    diagnosis_error += 'Не указан диагноз. '

                if diagnosis_date:
                    dt = datetime(int(diagnosis_date[0:4]), int(diagnosis_date[5:7]), int(diagnosis_date[8:10])).date()
                    if abs((dt - cda_sent_local_date).total_seconds()) <= 86400:
                        diagnosis_error += 'Дата установления диагноза равна дате СЭМДа. '
                else:
                    diagnosis_error += 'Не указана дата установления диагноза. '

                if is_in_cancer_register and rc_diagnosis_date and cda_sent_local_date and diagnosis_mkb10:
                    if cda_sent_local_date >= rc_diagnosis_date:
                        if diagnosis_code1077 == '1' and diagnosis_mkb10 != rc_diagnosis_mkb10:
                            diagnosis_error += 'Основной диагноз СЭМДа не равен диагнозу в канцер-регистре. '
                        if diagnosis_code1077 == '1' and diagnosis_mkb10 == rc_diagnosis_mkb10 and diagnosis_date:
                            dt = datetime(
                                int(diagnosis_date[0:4]), int(diagnosis_date[5:7]), int(diagnosis_date[8:10])
                            ).date()
                            if abs((dt - rc_diagnosis_date).total_seconds()) > 86400:
                                diagnosis_error += 'Дата установления диагноза СЭМДа не равна дате в канцер-регистре. '

                if not diagnosis_error:
                    diagnosis_error = 'Ok!'

                patient_semd = PatientSEMD(
                    id=sms.id,
                    ptn_id=ptn_id,
                    ptn_code=ptn_code,
                    rc_id=rc_id,
                    ehr_id=ehr_id,
                    rc_time=rc_time,
                    cda_sent_local_date=cda_sent_local_date,
                    internal_message_id=internal_message_id,
                    profile=profile,
                    soap_doc_type=soap_doc_type,
                    author_mo_oid=author_mo_oid,
                    author_mo_dpt_oid=author_mo_dpt_oid,
                    author_snils=author_snils,
                    author_post=author_post,
                    diagnosis_mkb10=diagnosis_mkb10,
                    diagnosis_date=diagnosis_date,
                    diagnosis_code197=diagnosis_code197,
                    diagnosis_code1076=diagnosis_code1076,
                    diagnosis_code1077=diagnosis_code1077,
                    is_cancer_diagnosis=is_cancer_diagnosis,
                    is_precancer_diagnosis=is_precancer_diagnosis,
                    diagnoses=diagnoses,
                    is_cancer_diagnoses=is_cancer_diagnoses,
                    is_precancer_diagnoses=is_precancer_diagnoses,
                    services=services,
                    cda_time=cda_time,
                    sms_type=sms_type,
                    is_in_cancer_register=is_in_cancer_register,
                    has_cancer_diagnosis=False,
                    has_precancer_diagnosis=False,
                    rc_diagnosis_mkb10=rc_diagnosis_mkb10,
                    rc_diagnosis_date=rc_diagnosis_date,
                    semd_content=semd_content,
                    content_error=content_error,
                    diagnosis_error=diagnosis_error
                )
                patient_semd.save()
                n += 1
                # if i >= 500:
                #     break

        # if i >= 500:
        #     break

    print(f"SEMD count = {n} (from {count})")

    print("-----------------------------------------------------------------------")
    print('Updating has_cancer_diagnosis flag...')
    query_body = """
        UPDATE
            api_patientsemd s
        SET
            has_cancer_diagnosis = TRUE
        WHERE EXISTS(
            SELECT
                has_cancer_diagnosis
            FROM
                api_patientsemd s2
            WHERE
                s2.ptn_id = s.ptn_id AND
                s2.is_cancer_diagnoses = TRUE
        )
    """
    with connection.cursor() as cursor:
        cursor.execute(query_body)

    print("-----------------------------------------------------------------------")
    print('Updating has_precancer_diagnosis flag...')
    query_body = """
        UPDATE
            api_patientsemd s
        SET
            has_precancer_diagnosis = TRUE
        WHERE EXISTS(
            SELECT
                has_precancer_diagnosis
            FROM
                api_patientsemd s2
            WHERE
                s2.ptn_id = s.ptn_id AND
                s2.is_precancer_diagnoses = TRUE
        )
    """
    with connection.cursor() as cursor:
        cursor.execute(query_body)

    print("-----------------------------------------------------------------------")


def get_diagnoses(internal_message_id) -> list:
    query_body = """
        SELECT
            regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:*[x:observation[x:value[@codeSystem="1.2.643.5.1.13.13.11.1005"]]]]', payload::xml, '{{x,urn:hl7-org:v3}}'), '<new/>'), '\n', ' ', 'g') as diagnoses
        FROM
            vimis_sending
        WHERE
            internal_message_id = '""" + internal_message_id + "'"

    with connections['egisz-db'].cursor() as cursor:
        cursor.execute(query_body)
        try:
            semd = cursor.fetchone()
        except Exception:
            semd = None

    if not semd:
        return list()

    xml_diagnoses = semd[0].split('<new/>')

    # Calculate diagnoses set
    diagnoses = set()
    for xml in xml_diagnoses:
        if not xml:
            continue
        try:
            parent = xmltodict.parse(xml)
            if not isinstance(parent, dict):
                continue
            for parent_key, parent_dict in parent.items():
                if not isinstance(parent_dict, dict):
                    continue
                row_diagnosis_code1076 = None
                parent_node_code_node = parent_dict.get('code', None)
                if parent_node_code_node and isinstance(parent_node_code_node, dict) and \
                        (parent_node_code_node.get('@codeSystem', None) == '1.2.643.5.1.13.13.11.1076' or
                         parent_node_code_node.get('@codeSystem', None) == '1.2.643.5.1.13.13.99.2.795'):
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
                                row_diagnosis_date = (
                                        observation_effective_time[0:4] + '-' +
                                        observation_effective_time[4:6] + '-' +
                                        observation_effective_time[6:8]
                                )

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
                                        row_diagnosis_code1076,
                                        row_diagnosis_code1077
                                    )
                                }
                            )

        except Exception:
            pass

    # Save records to result
    result_diagnoses = list()
    for diagnosis in diagnoses:
        d = {'mkb10': diagnosis[0]}
        if diagnosis[1]:
            d['date'] = diagnosis[1]
        if diagnosis[2]:
            d['code1076'] = diagnosis[2]
        if diagnosis[3]:
            d['code1077'] = diagnosis[3]
        result_diagnoses.append(d)

    return result_diagnoses


def get_diagnosis(diagnoses: list, code1077: Optional[str] = None,
                  code1076: Optional[str] = None, code197: Optional[str] = None,
                  date_expected: bool = False) -> Optional[dict]:
    for d in diagnoses:
        date = d.get('date', None)
        diagnosis_code197 = d.get('code197', None)
        diagnosis_code1076 = d.get('code1076', None)
        diagnosis_code1077 = d.get('code1077', None)
        if ((diagnosis_code197 == code197 if code197 else True) and
                (diagnosis_code1076 == code1076 if code1076 else True) and
                (diagnosis_code1077 == code1077 if code1077 else True) and
                (date is not None if date_expected else True)):
            return d

    return None


def get_content(internal_message_id: str, soap_doc_type: str) -> (dict, str):
    result_dict = None
    error_str = ''
    if soap_doc_type == '1':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SCOPORG"]]/x:entry/x:act/x:performer/x:assignedEntity/x:representedOrganization/x:id/@root', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as recipient,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SCOPORG"]]/x:entry/x:act/x:code[@codeSystem="1.2.643.5.1.13.13.11.1009"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as purpose,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as service,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1463"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as consultation_type
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'recipient': semd[0],
                'purpose': semd[1],
                'service': semd[2],
                'consultation_type': semd[3]
            }

    elif soap_doc_type == '2':
        query_body = """
            SELECT
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="1805"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as protocol,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="1806"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as conclusion,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="807"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as recommendation
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'protocol': semd[0] if len(semd[0]) >= INDICATOR_MIN_LENGTH else '',
                'conclusion': semd[1] if len(semd[1]) >= INDICATOR_MIN_LENGTH else '',
                'recommendation': semd[2] if len(semd[2]) >= INDICATOR_MIN_LENGTH else '',
            }

    elif soap_doc_type == '3':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1080"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as laboratory_tests
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'laboratory_tests': semd[0]
            }

    elif soap_doc_type == '4':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as histological_tests
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'histological_tests': semd[0]
            }

    elif soap_doc_type == '5':
        query_body = """
            SELECT
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="805"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as protocol,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="12193"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as protocol2,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="806"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as conclusion,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="837"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as conclusion2,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="807"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as recommendation
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'protocol': semd[0] + semd[1] if len(semd[0] + semd[1]) >= INDICATOR_MIN_LENGTH else '',
                'conclusion': semd[2] + semd[3] if len(semd[2] + semd[3]) >= INDICATOR_MIN_LENGTH else '',
                'recommendation': semd[4] if len(semd[4]) >= INDICATOR_MIN_LENGTH else '',
            }

    elif soap_doc_type == '6':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="vimisConsiliumProtocol"]]/x:entry/x:observation/x:effectiveTime/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as date,
                array_to_string(xpath('/x:ClinicalDocument/x:effectiveTime/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as date2,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="vimisConsiliumProtocol"]]/x:entry/x:observation/x:text/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ', '),'\n',' ','g') as number,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="CONSILIUM"]]/x:entry/x:observation[x:code[@code="11003"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ', '),'\n',' ','g') as number2,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1506"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as purpose,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.166"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as form,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.349"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as conclusion
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'date': (
                    semd[0][0:4] + '-' + semd[0][4:6] + '-' + semd[0][6:8]
                    if semd[0]
                    else semd[1][0:4] + '-' + semd[1][4:6] + '-' + semd[1][6:8]
                ),
                'number': semd[2] + semd[3],
                'purpose': semd[4],
                'form': semd[5],
                'conclusion': semd[6],
                'diagnostics': '',
                'laboratory_tests': '',
                'treatments': ''
            }

    elif soap_doc_type == '7':
        result_dict = 'Анализ не проводился.'

    elif soap_doc_type == '8':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="HOSP"]]/x:entry/x:encounter/x:effectiveTime/x:low/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as date_start,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="HOSP"]]/x:component/x:section[x:code[@code="PATIENTROUTE"]]/x:component/x:section[x:code[@code="DEPARTINFO"]]/x:entry/x:encounter/x:effectiveTime/x:low/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as date_start2,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.256"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as urgency,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="STATEADM"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1006"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as stateadm,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="HOSP"]]/x:entry/x:encounter/x:effectiveTime/x:high/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as date_end,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="HOSP"]]/x:component/x:section[x:code[@code="PATIENTROUTE"]]/x:component/x:section[x:code[@code="DEPARTINFO"]]/x:entry/x:encounter/x:effectiveTime/x:high/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as date_end2,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="STATEDIS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1006"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as statedis,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1046"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as result,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESCONS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as consultations,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESINSTR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as diagnostics,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESLAB"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1080"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as laboratory_tests,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESMOR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as morphology_tests,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="DRUG"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1367"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as sum_drug,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="2"][@codeSystem="1.2.643.5.1.13.13.11.1518"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.133"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as ray_therapy,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="41"][@codeSystem="1.2.643.5.1.13.13.11.1518"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.647"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as chemo_therapy,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="42"][@codeSystem="1.2.643.5.1.13.13.11.1518"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.407"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as hormone_therapy,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="SUR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as sur
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            if semd[0]:
                date_start = semd[0][0:4] + '-' + semd[0][4:6] + '-' + semd[0][6:8]
            else:
                date_start = semd[1].split(';')
                date_start = date_start[0]
                date_start = date_start[0:4] + '-' + date_start[4:6] + '-' + date_start[6:8]
            if semd[4]:
                date_end = semd[4][0:4] + '-' + semd[4][4:6] + '-' + semd[4][6:8]
            else:
                date_end = semd[5].split(';')
                date_end = date_end[len(date_end) - 1]
                date_end = date_end[0:4] + '-' + date_end[4:6] + '-' + date_end[6:8]
            result_dict = {
                'date_start': date_start,
                'urgency': semd[2],
                'stateadm': semd[3].split(';')[0],
                'date_end': date_end,
                'statedis': semd[6].split(';')[0],
                'result': semd[7],
                'consultations': semd[8],
                'diagnostics': semd[9],
                'laboratory_tests': semd[10],
                'morphology_tests': semd[11],
                'sum_drug': semd[12],
                'ray_therapy': semd[13],
                'chemo_therapy': semd[14],
                'hormone_therapy': semd[15],
                'sur': semd[16]
            }

    elif soap_doc_type == '9':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1080"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as cytological_tests
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'cytological_tests': semd[0]
            }

    elif soap_doc_type == '10':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SUR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as sur,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SUR"]]//x:effectiveTime/x:low/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as date_start,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SUR"]]//x:effectiveTime/x:high/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as date_end
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'sur': semd[0],
                'date_start': semd[1],
                'date_end': semd[2]
            }

    elif soap_doc_type == '11':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.144"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as late_reason,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.547"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ' ') as tnm,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.546"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as stage,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.143"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as side,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1486"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as morph_class,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.146"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as clinical_group,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.129"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as how_discover,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.901"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as gem_limph_class,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1487"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as topograph,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1477"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as loc_met,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:value[@codeSystem="1.2.643.5.1.13.13.99.2.127"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as loc_far_met,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[x:code[@code="12298"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as tumor_number,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[x:code[@code="12299"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as tumor_main,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.141"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as plural,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.583"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as tumor_state,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.761"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as blast_form,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.760"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as miel_phase,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.128"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as method,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1117"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as refined_method
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'late_reason': semd[0],
                'tnm': semd[1],
                'stage': semd[2],
                'side': semd[3],
                'morph_class': semd[4],
                'clinical_group': semd[5],
                'how_discover': semd[6],
                'gem_limph_class': semd[7],
                'topograph': semd[8],
                'loc_met': semd[9],
                'loc_far_met': semd[10],
                'tumor_number': semd[11],
                'tumor_main': semd[12],
                'plural': semd[13],
                'tumor_state': semd[14],
                'blast_form': semd[15],
                'miel_phase': semd[16],
                'method': semd[17],
                'refined_method': semd[18]
            }

    elif soap_doc_type == '12':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="AMBS"]]/x:entry/x:encounter/x:effectiveTime/x:low/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as date_start,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="AMBS"]]/x:entry/x:encounter/x:effectiveTime/x:high/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as date_end,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="AMBS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1007"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as order,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="AMBS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1046"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as result,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESCONS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as consultations,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESINSTR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as diagnostics,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESLAB"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1080"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as laboratory_tests,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESMOR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as morphology_tests,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="DRUG"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1367"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as sum_drug,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="SUR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ';') as sur
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'date_start': semd[0][0:4] + '-' + semd[0][4:6] + '-' + semd[0][6:8],
                'date_end': semd[1][0:4] + '-' + semd[1][4:6] + '-' + semd[1][6:8],
                'order': semd[2],
                'result': semd[3],
                'consultations': semd[4],
                'diagnostics': semd[5],
                'laboratory_tests': semd[6],
                'morphology_tests': semd[7],
                'sum_drug': semd[8],
                'sur': semd[9]
            }

    elif soap_doc_type == '13':
        result_dict = 'Анализ не проводился.'

    elif soap_doc_type == '16':
        result_dict = 'Анализ не проводился.'

    elif soap_doc_type == '20':
        query_body = """
            SELECT
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="805"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as protocol,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="806"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as conclusion,
                regexp_replace(array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="807"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', payload::xml, '{{x,urn:hl7-org:v3}}'), ' '),'\n',' ','g') as recommendation
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'protocol': semd[0] if len(semd[0]) >= INDICATOR_MIN_LENGTH else '',
                'conclusion': semd[1] if len(semd[1]) >= INDICATOR_MIN_LENGTH else '',
                'recommendation': semd[2] if len(semd[2]) >= INDICATOR_MIN_LENGTH else '',
            }

    elif soap_doc_type == '27':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SCOPORG"]]/x:entry/x:act/x:performer/x:assignedEntity/x:representedOrganization/x:id/@root', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as recipient,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as service
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'recipient': semd[0],
                'service': semd[1]
            }

    elif soap_doc_type == '37':
        query_body = """
            SELECT
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="ORGINFO"]]/x:entry/x:act/x:performer/x:assignedEntity/x:representedOrganization/x:id/@root', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as recipient,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.547"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ' ') as tnm,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.546"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as stage,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.143"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as side,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1486"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as morph_class,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.146"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as clinical_group,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.129"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as how_discover,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.901"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as gem_limph_class,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1487"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as topograph,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1477"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as loc_met,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:value[@codeSystem="1.2.643.5.1.13.13.99.2.127"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as loc_far_met,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[x:code[@code="12298"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as tumor_number,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[x:code[@code="12299"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/@value', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as tumor_main,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.141"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as plural,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.583"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as tumor_state,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.761"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as blast_form,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.760"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as miel_phase,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.128"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as method,
                array_to_string(xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1117"]/@displayName', payload::xml, '{{x,urn:hl7-org:v3}}'), ', ') as refined_method
            FROM
                vimis_sending
            WHERE
                internal_message_id = '""" + internal_message_id + "'"
        with connections['egisz-db'].cursor() as cursor:
            cursor.execute(query_body)
            try:
                semd = cursor.fetchone()
            except Exception:
                semd = None
        if semd:
            result_dict = {
                'recipient': semd[0],
                'tnm': semd[1],
                'stage': semd[2],
                'side': semd[3],
                'morph_class': semd[4],
                'clinical_group': semd[5],
                'how_discover': semd[6],
                'gem_limph_class': semd[7],
                'topograph': semd[8],
                'loc_met': semd[9],
                'loc_far_met': semd[10],
                'tumor_number': semd[11],
                'tumor_main': semd[12],
                'plural': semd[13],
                'tumor_state': semd[14],
                'blast_form': semd[15],
                'miel_phase': semd[16],
                'method': semd[17],
                'refined_method': semd[18]
            }

    else:
        result_dict = 'Анализ не проводился.'

    if isinstance(result_dict, dict):
        error_qty = 0
        for key in list(result_dict.keys()):
            if result_dict[key] == '':
                result_dict.pop(key, None)
                indicator = EXPECTED_INDICATORS[soap_doc_type].get(key, None)
                if indicator:
                    error_qty += 1
                    if not error_str:
                        error_str = f'Не указано: {indicator}'
                    else:
                        error_str += f', {indicator}'
        if not error_str:
            error_str = f'Ok!'
        else:
            error_str = f'Неполное заполнение -{error_qty}. ' + error_str
    elif isinstance(result_dict, str):
        error_str = f'{result_dict}'
        result_dict = dict()
    else:
        result_dict = dict()
        error_str = f'Ошибка валидации при отправке.'

    return result_dict, error_str


def check_diagnoses(diagnoses: list) -> (bool, bool):
    is_cancer_diagnoses = is_precancer_diagnoses = False

    for diagnosis in diagnoses:
        is_cancer_diagnosis, is_precancer_diagnosis = check_diagnosis(diagnosis)
        if is_cancer_diagnosis:
            is_cancer_diagnoses = True
        if is_precancer_diagnosis:
            is_precancer_diagnoses = True
        if is_cancer_diagnoses and is_precancer_diagnoses:
            break

    return is_cancer_diagnoses, is_precancer_diagnoses


def check_diagnosis(diagnosis: dict) -> (bool, bool):
    is_cancer_diagnosis = is_precancer_diagnosis = False

    mkb10 = diagnosis.get('mkb10', 'None')
    if not mkb10:
        return is_cancer_diagnosis, is_precancer_diagnosis

    is_cancer_diagnosis = mkb10 in CANCER_DIAGNOSES
    if is_cancer_diagnosis:
        return is_cancer_diagnosis, is_precancer_diagnosis

    for group_diagnoses in CANCER_DIAGNOSES:

        if isinstance(group_diagnoses, tuple):
            start_diagnosis = group_diagnoses[0]
            if len(group_diagnoses) == 2:
                end_diagnosis = group_diagnoses[1] + '.9'
            else:
                end_diagnosis = group_diagnoses[0] + '.9'

            is_cancer_diagnosis = (start_diagnosis <= mkb10 <= end_diagnosis)
            if is_cancer_diagnosis:
                return is_cancer_diagnosis, is_precancer_diagnosis

    is_precancer_diagnosis = mkb10 in PRECANCER_DIAGNOSES
    if is_precancer_diagnosis:
        return is_cancer_diagnosis, is_precancer_diagnosis

    for group_diagnoses in PRECANCER_DIAGNOSES:

        if isinstance(group_diagnoses, tuple):
            start_diagnosis = group_diagnoses[0]
            if len(group_diagnoses) == 2:
                end_diagnosis = group_diagnoses[1] + '.9'
            else:
                end_diagnosis = group_diagnoses[0] + '.9'

            is_precancer_diagnosis = (start_diagnosis <= mkb10 <= end_diagnosis)
            if is_precancer_diagnosis:
                return is_cancer_diagnosis, is_precancer_diagnosis

    return is_cancer_diagnosis, is_precancer_diagnosis

