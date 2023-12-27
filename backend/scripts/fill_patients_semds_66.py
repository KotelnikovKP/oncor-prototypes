import json
import math
from datetime import datetime, timezone
from typing import Optional

import xmltodict
from django.db import transaction, connection
from django.db.models import Q
from lxml import etree

from api.models.oncor_data_analytics_models import RcSemd, StatEhr
from api.models.orientdb_engine import orient_db_client
from api.models.semd_models import PatientSEMD

ATTACHMENTS_DIR = 'C:\\oncor\\attachments\\'
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
    semd_records = (
        RcSemd.objects
        .using('oncor-data-analytics')
        .filter(profile='ONCO')
        .filter(Q(cda_local_date__isnull=True) | Q(cda_local_date__gte=datetime(datetime.now().year, 1, 1)))
        # .filter(soap_doc_type='37')
    )

    count = semd_records.count()
    print(f'Found {count} semd.')

    i = n = 0
    # Get records for each semd in queryset
    for k in range(math.ceil(count / ITEMS_IN_ITERATION)):
        semd_records = (
            RcSemd.objects
            .using('oncor-data-analytics')
            .filter(profile='ONCO')
            .filter(Q(cda_local_date__isnull=True) | Q(cda_local_date__gte=datetime(datetime.now().year, 1, 1)))
            # .filter(soap_doc_type='37')
            .order_by('id')[k * ITEMS_IN_ITERATION:(k + 1) * ITEMS_IN_ITERATION]
        )
        with transaction.atomic():
            for semd in semd_records:
                i += 1
                print(f"{str(i).zfill(8)} from {count}: {semd.id}, {semd.rc_sms_id}, {semd.rc_cda_id}")

                ptn_id = semd.ptn_id
                rc_sms_id = semd.rc_sms_id
                rc_cda_id = semd.rc_cda_id
                is_external_semd = rc_cda_id is not None
                ptn_code = semd.ptn_code
                cda_local_date = semd.cda_local_date
                profile = semd.profile
                soap_doc_type = semd.soap_doc_type
                sms_summary = semd.sms_summary or dict()
                author_mo_oid = semd.author_mo_oid
                author_mo_dpt_oid = semd.author_mo_dpt_oid
                author_snils = semd.author_snils
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

                attachment = rc_time = send_task_step = send_task_status = None
                sms_status = cda_status = is_external_semd_sendable = None

                if rc_sms_id:
                    query_body = f'''
                        select 
                            cdaXml.digest as attachment,
                            timeRc,
                            cdaTask.step as step,
                            cdaTask.status as status,
                            instanceStatus.json as sms_status
                        from 
                            RcSms
                        where
                            @rid={rc_sms_id}
                    '''

                    try:
                        sms_record = orient_db_client.query(query_body, -1)[0]
                    except Exception:
                        sms_record = None

                    if sms_record:
                        attachment = sms_record.oRecordData.get('attachment', None)
                        rc_time = sms_record.oRecordData.get('timeRc', None)
                        if rc_time:
                            rc_time = datetime(rc_time.year, rc_time.month, rc_time.day, rc_time.hour,
                                               rc_time.minute, rc_time.second, tzinfo=timezone.utc)
                        send_task_step = sms_record.oRecordData.get('step', None)
                        send_task_status = sms_record.oRecordData.get('status', None)
                        sms_status = sms_record.oRecordData.get('sms_status', None)
                        try:
                            if sms_status:
                                sms_status = json.loads(sms_status)
                        except Exception:
                            sms_status = {'status': sms_status, 'level': 'UNKNOWN'}

                if rc_cda_id:
                    query_body = f'''
                        select 
                            cdaXml.digest as attachment,
                            timeRc,
                            cdaTask.step as step,
                            cdaTask.status as status,
                            instanceStatus.json as cda_status,
                            sendable
                        from 
                            RcCda
                        where
                            @rid={rc_cda_id}
                    '''

                    try:
                        sms_record = orient_db_client.query(query_body, -1)[0]
                    except Exception:
                        sms_record = None

                    if sms_record:
                        is_external_semd_sendable = sms_record.oRecordData.get('sendable', None)
                        if attachment is None:
                            attachment = sms_record.oRecordData.get('attachment', None)
                        if rc_time is None:
                            rc_time = sms_record.oRecordData.get('timeRc', None)
                            if rc_time:
                                rc_time = datetime(rc_time.year, rc_time.month, rc_time.day, rc_time.hour,
                                                   rc_time.minute, rc_time.second, tzinfo=timezone.utc)
                        if send_task_step is None:
                            send_task_step = sms_record.oRecordData.get('step', None)
                        if send_task_status is None:
                            send_task_status = sms_record.oRecordData.get('status', None)
                        cda_status = sms_record.oRecordData.get('cda_status', None)
                        try:
                            if cda_status:
                                cda_status = json.loads(cda_status)
                        except Exception:
                            cda_status = {'status': cda_status, 'level': 'UNKNOWN'}

                if cda_local_date is None and rc_time is not None:
                    cda_local_date = rc_time.date()

                if len(diagnoses) == 0 and attachment is not None:
                    diagnoses = get_diagnoses(attachment)

                is_cancer_diagnoses, is_precancer_diagnoses = check_diagnoses(diagnoses)

                diagnosis = None
                diagnosis_mkb10 = None
                diagnosis_date = None
                diagnosis_code197 = None
                diagnosis_code1076 = None
                diagnosis_code1077 = None
                is_cancer_diagnosis = is_precancer_diagnosis = False

                patient_diagnosis = None
                patient_diagnoses = (
                    StatEhr.objects
                    .using('oncor-data-analytics')
                    .filter(ptn_id=ptn_id, dz_mkb__isnull=False)
                    .order_by('-dz_date')
                )

                for pd in patient_diagnoses:
                    if pd.dz_date and (pd.dz_date <= cda_local_date if cda_local_date is not None else True):
                        patient_diagnosis = pd
                        break

                if not patient_diagnosis and len(patient_diagnoses):
                    patient_diagnosis = patient_diagnoses[0]

                if patient_diagnosis:
                    is_in_cancer_register = True
                    mkb10 = patient_diagnosis.dz_mkb.split('.')
                    if len(mkb10) > 1:
                        rc_diagnosis_mkb10 = mkb10[0] + '.' + str(int(mkb10[1]))
                    else:
                        rc_diagnosis_mkb10 = mkb10[0]
                    rc_diagnosis_mkb10_l1 = mkb10[0]
                    rc_diagnosis_date = patient_diagnosis.dz_date

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

                semd_content, content_error = get_content(attachment, soap_doc_type)

                diagnosis_error = ''
                if not diagnosis_mkb10:
                    diagnosis_error += 'Не указан диагноз. '

                if diagnosis_date:
                    if cda_local_date is not None:
                        dt = datetime(int(diagnosis_date[0:4]), int(diagnosis_date[5:7]), int(diagnosis_date[8:10])).date()
                        if abs((dt - cda_local_date).total_seconds()) <= 86400:
                            diagnosis_error += 'Дата установления диагноза равна дате СЭМДа. '
                else:
                    diagnosis_error += 'Не указана дата установления диагноза. '

                if is_in_cancer_register and rc_diagnosis_date and cda_local_date and diagnosis_mkb10:
                    if cda_local_date >= rc_diagnosis_date:
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
                    id=semd.id,
                    ptn_id=ptn_id,
                    ptn_code=ptn_code,
                    rc_sms_id=rc_sms_id,
                    rc_cda_id=rc_cda_id,
                    is_external_semd=is_external_semd,
                    is_external_semd_sendable=is_external_semd_sendable,
                    send_task_step=send_task_step,
                    send_task_status=send_task_status,
                    sms_status=sms_status,
                    cda_status=cda_status,
                    rc_time=rc_time,
                    cda_local_date=cda_local_date,
                    attachment=attachment,
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
                # if i >= 100:
                #     break

        # if i >= 100:
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


def get_diagnoses(attachment) -> list:

    def get_item_diagnoses(code197, code1076, code1077, diagnosis_date, item) -> set:
        item_diagnoses = set()
        if isinstance(item, list):
            for it in item:
                item_diagnoses = item_diagnoses.union(
                    get_item_diagnoses(code197, code1076, code1077, diagnosis_date, it)
                )

        elif isinstance(item, dict):
            local_code1076 = code1076
            local_code1077 = code1077
            local_diagnosis_date = diagnosis_date
            item_code = item.get('code', None)
            if isinstance(item_code, dict):
                code_system = item_code.get('@codeSystem', '')
                if code_system == '1.2.643.5.1.13.13.11.1076' or code_system == '1.2.643.5.1.13.13.99.2.795':
                    local_code1076 = item_code.get('@code', local_code1076)
                if code_system == '1.2.643.5.1.13.13.11.1077':
                    local_code1077 = item_code.get('@code', local_code1077)
            item_effective_time = item.get('effectiveTime', None)
            if isinstance(item_effective_time, dict):
                local_effective_time = item_effective_time.get('@value', None)
                if isinstance(local_effective_time, str):
                    local_diagnosis_date = (
                        local_effective_time[0:4] + '-' +
                        local_effective_time[4:6] + '-' +
                        local_effective_time[6:8]
                    )
            code_system = item.get('@codeSystem', '')
            if code_system == '1.2.643.5.1.13.13.11.1005':
                local_mkb10 = item.get('@code', 'UNKNOWN')
                item_diagnoses = item_diagnoses.union(
                    {
                        (
                            local_mkb10,
                            local_diagnosis_date,
                            local_code1076,
                            local_code1077,
                            code197
                        )
                    }
                )
            for it in item.keys():
                item_diagnoses = item_diagnoses.union(
                    get_item_diagnoses(code197, local_code1076, local_code1077, local_diagnosis_date, item[it])
                )

        return item_diagnoses

    attachment_file = ATTACHMENTS_DIR + attachment[:2] + '\\' + attachment

    try:
        with open(attachment_file, 'r', encoding='utf-8') as f:
            xml_dict = f.read()
        xml_dict = xmltodict.parse(xml_dict)
    except Exception as e:
        print(f"{type(e)}: {str(e)}")
        return list()

    try:
        components = xml_dict['ClinicalDocument']['component']['structuredBody']['component']
        if not isinstance(components, list):
            return list()
    except Exception as e:
        print(f"{type(e)}: {str(e)}")
        return list()

    # Calculate diagnoses set
    diagnoses = set()

    for component in components:
        try:
            section = component['section']
            if not isinstance(section, dict):
                continue
        except Exception as e:
            print(f"{type(e)}: {str(e)}")
            continue

        code = section.get('code', None)
        if isinstance(code, dict):
            section_code197 = code.get('@code', None)
        else:
            section_code197 = None

        section_diagnoses = get_item_diagnoses(section_code197, None, None, None, section)

        diagnoses = diagnoses.union(section_diagnoses)

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
        if diagnosis[4]:
            d['code197'] = diagnosis[4]
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


def get_content(attachment: str, soap_doc_type: str) -> (dict, str):
    if attachment is None:
        return dict(), 'Нет указан файл с xml СЭМДа.'

    result_dict = None
    error_str = ''

    attachment_file = ATTACHMENTS_DIR + attachment[:2] + '\\' + attachment

    try:
        xml_dict = etree.parse(attachment_file, parser=etree.XMLParser())
    except Exception as e:
        print(f"{type(e)}: {str(e)}")
        return dict(), 'Нет файла с xml СЭМДа, либо ошибка парсинга xml СЭМДа.'

    if soap_doc_type == '1':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SCOPORG"]]/x:entry/x:act/x:performer/x:assignedEntity/x:representedOrganization/x:id/@root', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SCOPORG"]]/x:entry/x:act/x:code[@codeSystem="1.2.643.5.1.13.13.11.1009"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value3 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1463"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'recipient': value0,
            'purpose': value1,
            'service': value2,
            'consultation_type': value3
        }
        
    elif soap_doc_type == '2':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="1805"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="1806"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="807"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'protocol': value0 if len(value0) >= INDICATOR_MIN_LENGTH else '',
            'conclusion': value1 if len(value1) >= INDICATOR_MIN_LENGTH else '',
            'recommendation': value2 if len(value2) >= INDICATOR_MIN_LENGTH else '',
        }

    elif soap_doc_type == '3':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1080"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'laboratory_tests': value0
        }

    elif soap_doc_type == '4':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'histological_tests': value0
        }

    elif soap_doc_type == '5':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="805"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="12193"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="806"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value3 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="837"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value4 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="807"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'protocol': value0 + value1 if len(value0 + value1) >= INDICATOR_MIN_LENGTH else '',
            'conclusion': value2 + value3 if len(value2 + value3) >= INDICATOR_MIN_LENGTH else '',
            'recommendation': value4 if len(value4) >= INDICATOR_MIN_LENGTH else '',
        }

    elif soap_doc_type == '6':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="vimisConsiliumProtocol"]]/x:entry/x:observation/x:effectiveTime/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:effectiveTime/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="vimisConsiliumProtocol"]]/x:entry/x:observation/x:text/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value3 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="CONSILIUM"]]/x:entry/x:observation[x:code[@code="11003"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value4 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1506"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value5 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.166"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value6 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.349"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'date': (
                value0[0:4] + '-' + value0[4:6] + '-' + value0[6:8]
                if value0
                else value1[0:4] + '-' + value1[4:6] + '-' + value1[6:8]
            ),
            'number': value2 + value3,
            'purpose': value4,
            'form': value5,
            'conclusion': value6,
            'diagnostics': '',
            'laboratory_tests': '',
            'treatments': ''
        }

    elif soap_doc_type == '7':
        result_dict = 'Анализ не проводился.'

    elif soap_doc_type == '8':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="HOSP"]]/x:entry/x:encounter/x:effectiveTime/x:low/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="HOSP"]]/x:component/x:section[x:code[@code="PATIENTROUTE"]]/x:component/x:section[x:code[@code="DEPARTINFO"]]/x:entry/x:encounter/x:effectiveTime/x:low/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.256"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value3 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="STATEADM"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1006"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value4 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="HOSP"]]/x:entry/x:encounter/x:effectiveTime/x:high/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value5 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="HOSP"]]/x:component/x:section[x:code[@code="PATIENTROUTE"]]/x:component/x:section[x:code[@code="DEPARTINFO"]]/x:entry/x:encounter/x:effectiveTime/x:high/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value6 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="STATEDIS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1006"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value7 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1046"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value8 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESCONS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value9 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESINSTR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value10 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESLAB"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1080"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value11 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESMOR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value12 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="DRUG"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1367"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value13 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="2"][@codeSystem="1.2.643.5.1.13.13.11.1518"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.133"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value14 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="41"][@codeSystem="1.2.643.5.1.13.13.11.1518"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.647"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value15 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="42"][@codeSystem="1.2.643.5.1.13.13.11.1518"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.407"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value16 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="SUR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        if value0:
            date_start = value0[0:4] + '-' + value0[4:6] + '-' + value0[6:8]
        else:
            date_start = value1.split(';')
            date_start = date_start[0]
            date_start = date_start[0:4] + '-' + date_start[4:6] + '-' + date_start[6:8]
        if value4:
            date_end = value4[0:4] + '-' + value4[4:6] + '-' + value4[6:8]
        else:
            date_end = value5.split(';')
            date_end = date_end[len(date_end) - 1]
            date_end = date_end[0:4] + '-' + date_end[4:6] + '-' + date_end[6:8]
        result_dict = {
            'date_start': date_start,
            'urgency': value2,
            'stateadm': value3.split(';')[0],
            'date_end': date_end,
            'statedis': value6.split(';')[0],
            'result': value7,
            'consultations': value8,
            'diagnostics': value9,
            'laboratory_tests': value10,
            'morphology_tests': value11,
            'sum_drug': value12,
            'ray_therapy': value13,
            'chemo_therapy': value14,
            'hormone_therapy': value15,
            'sur': value16
        }

    elif soap_doc_type == '9':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1080"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'cytological_tests': value0
        }

    elif soap_doc_type == '10':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SUR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SUR"]]//x:effectiveTime/x:low/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SUR"]]//x:effectiveTime/x:high/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'sur': value0,
            'date_start': value1,
            'date_end': value2
        }

    elif soap_doc_type == '11':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.144"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.547"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.546"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value3 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.143"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value4 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1486"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value5 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.146"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value6 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.129"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value7 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.901"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value8 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1487"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value9 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1477"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value10 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:value[@codeSystem="1.2.643.5.1.13.13.99.2.127"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value11 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[x:code[@code="12298"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value12 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[x:code[@code="12299"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value13 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.141"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value14 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.583"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value15 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.761"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value16 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.760"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value17 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.128"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value18 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1117"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'late_reason': value0,
            'tnm': value1,
            'stage': value2,
            'side': value3,
            'morph_class': value4,
            'clinical_group': value5,
            'how_discover': value6,
            'gem_limph_class': value7,
            'topograph': value8,
            'loc_met': value9,
            'loc_far_met': value10,
            'tumor_number': value11,
            'tumor_main': value12,
            'plural': value13,
            'tumor_state': value14,
            'blast_form': value15,
            'miel_phase': value16,
            'method': value17,
            'refined_method': value18
        }

    elif soap_doc_type == '12':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="AMBS"]]/x:entry/x:encounter/x:effectiveTime/x:low/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="AMBS"]]/x:entry/x:encounter/x:effectiveTime/x:high/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="AMBS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1007"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value3 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="AMBS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1046"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value4 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESCONS"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value5 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESINSTR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value6 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESLAB"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1080"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value7 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="RESMOR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value8 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="DRUG"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1367"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value9 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="SUR"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'date_start': value0[0:4] + '-' + value0[4:6] + '-' + value0[6:8],
            'date_end': value1[0:4] + '-' + value1[4:6] + '-' + value1[6:8],
            'order': value2,
            'result': value3,
            'consultations': value4,
            'diagnostics': value5,
            'laboratory_tests': value6,
            'morphology_tests': value7,
            'sum_drug': value8,
            'sur': value9
        }

    elif soap_doc_type == '13':
        result_dict = 'Анализ не проводился.'

    elif soap_doc_type == '16':
        result_dict = 'Анализ не проводился.'

    elif soap_doc_type == '20':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="805"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="806"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[x:code[@code="807"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/text()', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'protocol': value0 if len(value0) >= INDICATOR_MIN_LENGTH else '',
            'conclusion': value1 if len(value1) >= INDICATOR_MIN_LENGTH else '',
            'recommendation': value2 if len(value2) >= INDICATOR_MIN_LENGTH else '',
        }

    elif soap_doc_type == '27':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="SCOPORG"]]/x:entry/x:act/x:performer/x:assignedEntity/x:representedOrganization/x:id/@root', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component//x:*[@codeSystem="1.2.643.5.1.13.13.11.1070"]/@code', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'recipient': value0,
            'service': value1
        }

    elif soap_doc_type == '37':
        value0 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="ORGINFO"]]/x:entry/x:act/x:performer/x:assignedEntity/x:representedOrganization/x:id/@root', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value1 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.547"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value2 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.546"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value3 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.143"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value4 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1486"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value5 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.146"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value6 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.129"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value7 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.901"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value8 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1487"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value9 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1477"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value10 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:value[@codeSystem="1.2.643.5.1.13.13.99.2.127"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value11 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[x:code[@code="12298"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value12 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[x:code[@code="12299"][@codeSystem="1.2.643.5.1.13.13.99.2.166"]]/x:value/@value', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value13 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.141"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value14 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.583"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value15 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.761"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value16 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.760"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value17 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.99.2.128"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        value18 = ' '.join(xml_dict.xpath('/x:ClinicalDocument/x:component/x:structuredBody/x:component/x:section[x:code[@code="DGN"]]//x:*[@codeSystem="1.2.643.5.1.13.13.11.1117"]/@displayName', namespaces={'x': 'urn:hl7-org:v3'})).replace('\n', ' ').replace('\r', ' ')
        result_dict = {
            'recipient': value0,
            'tnm': value1,
            'stage': value2,
            'side': value3,
            'morph_class': value4,
            'clinical_group': value5,
            'how_discover': value6,
            'gem_limph_class': value7,
            'topograph': value8,
            'loc_met': value9,
            'loc_far_met': value10,
            'tumor_number': value11,
            'tumor_main': value12,
            'plural': value13,
            'tumor_state': value14,
            'blast_form': value15,
            'miel_phase': value16,
            'method': value17,
            'refined_method': value18
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

