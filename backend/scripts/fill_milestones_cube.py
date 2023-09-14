from datetime import date, datetime

from django.db import connection, transaction
from django.utils import formats, translation

from api.models.orientdb_engine import orient_db_client
from api.models.semd_models import PatientDiagnosisMilestones, OncorSettings
from api.utils.directories_utils import expand_diagnoses_only_codes, expand_services_only_codes


def run(*args):
    print("-----------------------------------------------------------------------")
    print("Procedure FILL Patient-Diagnosis cube was started!")
    if 'erase-cube' in args:
        print("Found 'erase-cube' parameter, it is starting delete cubes records...")
        with transaction.atomic():
            patient_diagnosis = PatientDiagnosisMilestones.objects.all()
            patient_diagnosis.delete()
        print("    Patient-Diagnosis cube has been cleaned")

    if 'only-fill-milestones' not in args:
        # Create patient-diagnosis in cube
        print("Start stage of creating patient-diagnosis in cube...")
        query_body = """
            INSERT INTO
                api_patientdiagnosismilestones (ptn_id, ptn_code, ptn_tags, diagnosis_mkb10, diagnosis_date)
            SELECT
                  sd.ptn_id, sd.ptn_code, sd.ptn_tags, sd.diagnosis_mkb10, sd.min_diagnosis_date
            FROM
               (SELECT
                    ptn_id, ptn_code, ptn_tags, diagnosis_mkb10, MIN(diagnosis_date) AS min_diagnosis_date
                FROM
                    api_semddiagnosis
                GROUP BY
                    ptn_id, ptn_code, ptn_tags, diagnosis_mkb10) as sd
            WHERE
                sd.min_diagnosis_date IS NOT NULL
        """
        with connection.cursor() as cursor:
            cursor.execute(query_body)

        print(f"Stage of creating patient-diagnosis in cube has finished. "
              f"{PatientDiagnosisMilestones.objects.all().count()} patient-diagnosis were created.")

        # Fill ptm_mo_oid

        print("Start stage of getting mo_oid of patients...")
        # Save mo_oid of patient
        query_body = """
            SELECT 
                @rid, 
                observer.nsiMedOrg.oid as mo_oid
            FROM 
                ptn
        """
        patients = orient_db_client.query(query_body, -1)
        patients_mo_oid = dict()
        for patient in patients:
            patients_mo_oid[str(patient.oRecordData.get('rid', None))] = patient.oRecordData.get('mo_oid', None)

        print(f"Stage of getting mo_oid of patients has finished. "
              f"{len(patients_mo_oid)} mo_oids of patient were get.")

        print("Start stage of saving mo_oid of patients in cube...")
        with transaction.atomic():
            patient_diagnoses = PatientDiagnosisMilestones.objects.all()
            for patient_diagnosis in patient_diagnoses:
                patient_diagnosis.ptn_mo_oid = \
                    patients_mo_oid.get(patient_diagnosis.ptn_id, None)
                patient_diagnosis.save()
        print("Stage of saving mo_oid of patients in cube has finished.")

    else:
        print("Found 'only-fill-milestones' parameter, continue without the recreating cube records")

    # Fill milestones
    rule_diagnoses_services = get_rule_diagnoses_services()
    with transaction.atomic():
        patient_diagnoses = PatientDiagnosisMilestones.objects.all()
        i = 0
        for patient_diagnosis in patient_diagnoses:
            milestones = dict()
            for rule_diagnoses_service in rule_diagnoses_services:
                if not rule_diagnoses_service['diagnoses'].count(patient_diagnosis.diagnosis_mkb10):
                    continue

                # Get referrals
                query_body = """
                    SELECT
                        time_rc
                    FROM
                        api_semdservice
                    WHERE
                        document_type IN ('1', '27') AND
                        ptn_id='""" + patient_diagnosis.ptn_id + """' AND
                        service_code IN (""" + ','.join(rule_diagnoses_service['services']) + """) AND
                        time_rc>='""" + patient_diagnosis.diagnosis_date.strftime('%Y-%m-%d') + """'
                    ORDER BY
                        time_rc
                    LIMIT 1
                    """
                with connection.cursor() as cursor:
                    cursor.execute(query_body)
                    semd_services = cursor.fetchall()

                if len(semd_services) == 1:
                    milestones[rule_diagnoses_service['code'] + ':нап'] = \
                        (semd_services[0][0].date() - patient_diagnosis.diagnosis_date).days

                # Get referrals
                query_body = """
                    SELECT
                        service_date
                    FROM
                        api_semdservice
                    WHERE
                        document_type IN ('2', '3', '4', '9', '12', '20') AND
                        ptn_id='""" + patient_diagnosis.ptn_id + """' AND
                        service_code IN (""" + ','.join(rule_diagnoses_service['services']) + """) AND
                        service_date>='""" + patient_diagnosis.diagnosis_date.strftime('%Y-%m-%d') + """'
                    ORDER BY
                        service_date
                    LIMIT 1
                    """
                with connection.cursor() as cursor:
                    cursor.execute(query_body)
                    semd_services = cursor.fetchall()

                if len(semd_services) == 1:
                    milestones[rule_diagnoses_service['code'] + ':исп'] = \
                        (semd_services[0][0] - patient_diagnosis.diagnosis_date).days

            if milestones:
                patient_diagnosis.diagnosis_milestones = milestones
                patient_diagnosis.save()

            print(f"{i}: {patient_diagnosis.ptn_id} {patient_diagnosis.diagnosis_mkb10} - {len(milestones)} | {milestones}")
            i += 1


def get_rule_diagnoses_services(check_date: date = datetime.now().date()) -> list:
    result = list()

    def find_rule_diagnoses_service(diagnoses: set, services: set) -> int | None:
        for result_idx, result_item in enumerate(result):
            if result_item['diagnoses'] == diagnoses and result_item['services'] == services:
                return result_idx
        return None

    try:
        orders = OncorSettings.objects.get(code='orders_rules').value
    except:
        orders = list()

    if not orders:
        return []

    date_formats = formats.get_format("DATE_INPUT_FORMATS", lang=translation.get_language())
    date_formats.append('%d.%m.%Y')

    try:
        for order in orders:
            if not isinstance(order, dict):
                continue

            order_code = order.get('code', None)
            if not order_code or not isinstance(order_code, str):
                continue

            order_valid = order.get('order_valid', None)
            if order_valid and isinstance(order_valid, dict):
                order_valid_from = order_valid.get('from', None)
                order_valid_to = order_valid.get('to', None)
            else:
                order_valid_from = None
                order_valid_to = None

            if order_valid_from:
                is_date_error = True
                for date_format in date_formats:
                    try:
                        order_valid_from = datetime.strptime(order_valid_from, date_format).date()
                        is_date_error = False
                        break
                    except:
                        pass
                if is_date_error:
                    order_valid_from = None

            if order_valid_to:
                is_date_error = True
                for date_format in date_formats:
                    try:
                        order_valid_to = datetime.strptime(order_valid_to, date_format).date()
                        is_date_error = False
                        break
                    except:
                        pass
                if is_date_error:
                    order_valid_to = None

            if not order_valid_from or not isinstance(order_valid_from, date):
                continue

            if order_valid_from > check_date:
                continue

            if order_valid_to and isinstance(order_valid_to, date) and order_valid_to < check_date:
                continue

            rules = order.get('rules', None)
            if not rules or not isinstance(rules, list):
                continue

            for rule in rules:
                if not isinstance(rule, dict):
                    continue

                rule_code = rule.get('code', None)
                if not rule_code or not isinstance(rule_code, str):
                    continue

                rule_diagnoses = rule.get('diagnoses', None)
                if not rule_diagnoses or not isinstance(rule_diagnoses, str):
                    continue

                rule_expanded_diagnoses = expand_diagnoses_only_codes(rule_diagnoses)

                rule_mandatory_services = rule.get('mandatory_services', None)
                if not rule_mandatory_services or not isinstance(rule_mandatory_services, list):
                    continue

                for rule_mandatory_service in rule_mandatory_services:
                    if not rule_mandatory_service or not isinstance(rule_mandatory_service, dict):
                        continue

                    rule_services_code = rule_mandatory_service.get('code', None)
                    if not rule_services_code or not isinstance(rule_services_code, str):
                        continue

                    rule_services = rule_mandatory_service.get('services', None)
                    if not rule_services or not isinstance(rule_services, list):
                        continue

                    rule_expanded_services = expand_services_only_codes(rule_services)
                    if not rule_services:
                        continue

                    idx = find_rule_diagnoses_service(rule_expanded_diagnoses, rule_expanded_services)
                    if idx is None:
                        result.append({
                            'services': rule_expanded_services,
                            'diagnoses': rule_expanded_diagnoses,
                            'order_valid_from': order_valid_from,
                            'code': order_code + '|' + rule_code + '|' + rule_services_code,
                        })
                    else:
                        if order_valid_from > result[idx]['order_valid_from']:
                            result[idx]['order_valid_from'] = order_valid_from
                            result[idx]['code'] = order_code + '|' + rule_code + '|' + rule_services_code

        for i, item in enumerate(result):
            item['services'] = sorted(item['services'])
            item['services'] = ["'" + service + "'" for service in item['services']]
            item['diagnoses'] = list(item['diagnoses'])
            item['diagnoses'] = sorted(item['diagnoses'])

    except Exception as e:
        print(str(e))

    return result
