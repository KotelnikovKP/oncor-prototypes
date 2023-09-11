import time
from collections import OrderedDict

from django.db import connections
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.models.semd_models import OncorSettings
from api.serializers.order_serializers import F14ListSerializer
from api.serializers.serializers import PaginationListSerializer


class GetF14Service:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> F14ListSerializer:
        """
            Retrieve orders F14 report
        """

        # Get query params
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        print(date_from, type(date_from))
        print(date_to, type(date_to))

        # Generate sceleton of report
        result = get_grouped_rule_services()

        f14_list_serializer = view.get_serializer(result, many=True)

        count = len(result)
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
        return_serializer = F14ListSerializer(
            data={
                'retCode': 0,
                'retMsg': 'Ok' if count > 0 else 'Result set is empty',
                'result': f14_list_serializer.data,
                'retExtInfo': pagination_list_serializer.data,
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


def get_grouped_rule_services() -> list:
    result = list()

    def find_rule_service(services_group: str, services: set) -> int | None:
        for i, item in enumerate(result):
            if item['services_group'] == services_group and item['services'] == services:
                return i
        return None

    try:
        orders = OncorSettings.objects.get(code='orders_rules').value
    except:
        orders = list()

    if not orders:
        return []

    try:
        for order in orders:
            if not isinstance(order, dict):
                continue

            order_name = order.get('order_name', None)
            order_author = order.get('order_author', None)
            order_valid = order.get('order_valid', None)
            if order_valid and isinstance(order_valid, dict):
                order_valid_from = order_valid.get('from', None)
                order_valid_to = order_valid.get('to', None)
            else:
                order_valid_from = None
                order_valid_to = None

            rules = order.get('rules', None)
            if not rules or not isinstance(rules, list):
                break

            for rule in rules:
                if not isinstance(rule, dict):
                    continue

                rule_name = rule.get('name', None)
                rule_text = rule.get('text', None)

                rule_diagnoses = rule.get('diagnoses', None)
                if not rule_diagnoses or not isinstance(rule_diagnoses, str):
                    continue

                rule_diagnoses = expand_diagnoses(rule_diagnoses)

                rule_mandatory_services = rule.get('mandatory_services', None)
                if not rule_mandatory_services or not isinstance(rule_mandatory_services, list):
                    continue

                for rule_mandatory_service in rule_mandatory_services:
                    if not rule_mandatory_service or not isinstance(rule_mandatory_service, dict):
                        continue

                    rule_services_group = rule_mandatory_service.get('group', None)
                    rule_services_period = rule_mandatory_service.get('period', None)
                    rule_services_name = rule_mandatory_service.get('name', None)
                    rule_services = rule_mandatory_service.get('services', None)

                    if not rule_services or not isinstance(rule_services, list):
                        continue

                    rule_services = expand_services(rule_services)

                    if not rule_services:
                        continue

                    idx = find_rule_service(rule_services_group, rule_services)
                    if idx is None:
                        result.append(OrderedDict([
                            ('row_number', None),
                            ('mo_oid', None),
                            ('mo_name', None),
                            ('services_group', rule_services_group),
                            ('services_period', rule_services_period),
                            ('services_name', rule_services_name),
                            ('services', rule_services),
                            ('patients_count', None),
                            ('referrals_count', None),
                            ('protocols_count', None),
                            ('diagnoses', rule_diagnoses),
                            ('order_rules', [
                                OrderedDict([
                                    ('order_name', order_name),
                                    ('order_valid_from', order_valid_from),
                                    ('order_valid_to', order_valid_to),
                                    ('order_author', order_author),
                                    ('rule_name', rule_name),
                                    ('rule_text', rule_text),
                                ])
                            ]),
                        ]))
                    else:
                        result[idx]['diagnoses'] = result[idx]['diagnoses'].union(rule_diagnoses)
                        result[idx]['order_rules'].append(
                            OrderedDict([
                                ('order_name', order_name),
                                ('order_valid_from', order_valid_from),
                                ('order_valid_to', order_valid_to),
                                ('order_author', order_author),
                                ('rule_name', rule_name),
                                ('rule_text', rule_text),
                            ])
                        )
        for item in result:
            item['services'] = sorted(item['services'], key=lambda x: x[0])
            item['services'] = [
                OrderedDict([
                    ('service_code', srv[0]),
                    ('service_name', srv[1]),
                ])
                for srv in item['services']
            ]
            item['diagnoses'] = sorted(item['diagnoses'], key=lambda x: x[0])
            item['diagnoses'] = [
                OrderedDict([
                    ('diagnosis_code', dz[0]),
                    ('diagnosis_name', dz[1]),
                ])
                for dz in item['diagnoses']
            ]

        result = sorted(result, key=lambda x: x['services_group'])
        for i, item in enumerate(result):
            item['row_number'] = i + 1

    except Exception as e:
        print(str(e))

    return result


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
