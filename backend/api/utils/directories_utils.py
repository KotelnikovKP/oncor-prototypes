from collections import OrderedDict

from django.db import connections


def expand_diagnoses(diagnoses_str: str) -> set:
    result_set = set()

    diagnoses = diagnoses_str.split(',')
    for diagnosis in diagnoses:
        diagnosis = diagnosis.strip()
        if not diagnosis:
            continue

        diagnosis_from_to = diagnosis.split('-')
        if len(diagnosis_from_to) == 1:
            diagnosis_from = diagnosis_from_to[0].strip()
            diagnosis_to = diagnosis_from + 'я'
        else:
            diagnosis_from = diagnosis_from_to[0].strip()
            diagnosis_to = diagnosis_from_to[1].strip()

        query_body = """
            SELECT
                code,
                name
            FROM 
                directory
            WHERE
                passport_oid='1.2.643.5.1.13.13.11.1005' AND
                NOT code like '%-%' AND
                code>='""" + diagnosis_from + """' AND
                code<'""" + diagnosis_to + "'"
        with connections['rosminzdrav-directories'].cursor() as cursor:
            cursor.execute(query_body)
            directory_diagnoses = cursor.fetchall()

        for directory_diagnosis in directory_diagnoses:
            if directory_diagnosis[0]:
                result_set = result_set.union({(directory_diagnosis[0], directory_diagnosis[1])})

    return result_set


def expand_diagnoses_only_codes(diagnoses_str: str) -> set:
    result_set = set()

    diagnoses = diagnoses_str.split(',')
    for diagnosis in diagnoses:
        diagnosis = diagnosis.strip()
        if not diagnosis:
            continue

        diagnosis_from_to = diagnosis.split('-')
        if len(diagnosis_from_to) == 1:
            diagnosis_from = diagnosis_from_to[0].strip()
            diagnosis_to = diagnosis_from + 'я'
        else:
            diagnosis_from = diagnosis_from_to[0].strip()
            diagnosis_to = diagnosis_from_to[1].strip()

        query_body = """
            SELECT
                code
            FROM 
                directory
            WHERE
                passport_oid='1.2.643.5.1.13.13.11.1005' AND
                NOT code like '%-%' AND
                code>='""" + diagnosis_from + """' AND
                code<'""" + diagnosis_to + "'"
        with connections['rosminzdrav-directories'].cursor() as cursor:
            cursor.execute(query_body)
            directory_diagnoses = cursor.fetchall()

        for directory_diagnosis in directory_diagnoses:
            if directory_diagnosis[0]:
                result_set = result_set.union({directory_diagnosis[0]})

    return result_set


def expand_services(services: list) -> set:
    result_set = set()

    quoted_services = ["'" + service.strip() + "'" for service in services]

    query_body = """
        SELECT
            code,
            name
        FROM 
            directory
        WHERE
            passport_oid='1.2.643.5.1.13.13.11.1070' AND
            code in (""" + ','.join(quoted_services) + ')'
    with connections['rosminzdrav-directories'].cursor() as cursor:
        cursor.execute(query_body)
        directory_services = cursor.fetchall()

    for directory_service in directory_services:
        if directory_service[0]:
            result_set = result_set.union({(directory_service[0], directory_service[1])})

    return result_set


def expand_services_only_codes(services: list) -> set:
    result_set = set()

    quoted_services = ["'" + service.strip() + "'" for service in services]

    query_body = """
        SELECT
            code
        FROM 
            directory
        WHERE
            passport_oid='1.2.643.5.1.13.13.11.1070' AND
            code in (""" + ','.join(quoted_services) + ')'
    with connections['rosminzdrav-directories'].cursor() as cursor:
        cursor.execute(query_body)
        directory_services = cursor.fetchall()

    for directory_service in directory_services:
        if directory_service[0]:
            result_set = result_set.union({directory_service[0]})

    return result_set


def expand_mos(mo_oids: set) -> list:
    query_body = """
        SELECT
            oid,
            name
        FROM 
            directory
        WHERE
            passport_oid='1.2.643.5.1.13.13.11.1461' AND
            oid in (""" + ','.join(["'" + mo_oid + "'" for mo_oid in mo_oids]) + """)
        ORDER BY
            name
    """
    with connections['rosminzdrav-directories'].cursor() as cursor:
        cursor.execute(query_body)
        directory_mos = cursor.fetchall()

    result = [
        OrderedDict([
            ('mo_oid', directory_mo[0]),
            ('mo_name', directory_mo[1]),
        ])
        for directory_mo in directory_mos
    ]

    return result


