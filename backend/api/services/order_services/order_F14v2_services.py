import time
from collections import OrderedDict
from datetime import datetime, date

from django.db import connection
from django.utils import formats, translation
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.models.semd_models import OncorSettings
from api.serializers.order_serializers import F14v2ListSerializer
from api.serializers.serializers import PaginationListSerializer
from api.utils.directories_utils import expand_diagnoses, expand_services, expand_mos


class GetF14v2Service:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> F14v2ListSerializer:
        """
            Retrieve orders F14 v.2 report
        """

        s_all = time.perf_counter()

        # Get query params
        date_from_str = request.query_params.get('date_from', None)
        date_to_str = request.query_params.get('date_to', None)
        date_from = None
        date_to = None

        if not date_from_str or not date_to_str:
            raise ValidationError(f"Period parameters must have filled", code='period')

        date_formats = formats.get_format("DATE_INPUT_FORMATS", lang=translation.get_language())
        date_formats.append('%d.%m.%Y')

        is_date_from_error = True
        for date_format in date_formats:
            try:
                date_from = datetime.strptime(date_from_str, date_format).date()
                is_date_from_error = False
                break
            except:
                pass
        if is_date_from_error:
            raise ValidationError(f"Value of period date from parameter ({date_from_str}) is not valid. "
                                  f"See valid date formats: " + '; '.join(["'" + f + "'" for f in date_formats]),
                                  code='date_from')

        is_date_to_error = True
        for date_format in date_formats:
            try:
                date_to = datetime.strptime(date_to_str, date_format).date()
                is_date_to_error = False
                break
            except:
                pass
        if is_date_to_error:
            raise ValidationError(f"Value of period date to parameter ({date_to_str}) is not valid. "
                                  f"See valid date formats: " + '; '.join(["'" + f + "'" for f in date_formats]),
                                  code='date_to')

        if date_to < date_from:
            raise ValidationError(f"Period is empty: date from ({date_from}) is greater than date to ({date_to})",
                                  code='period')

        # Generate sceleton of report
        result = get_grouped_rule_services(date_from, date_to)

        # Get report indicators
        result = get_report_indicators(result, date_from, date_to)

        f14v2_list_serializer = view.get_serializer(result)

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

        elapsed = time.perf_counter() - s_all

        ret_msg = 'Ok' if count > 0 else 'Result set is empty'
        ret_msg += f", processing time = {elapsed: 0.12f}"

        # Formate response schema
        return_serializer = F14v2ListSerializer(
            data={
                'retCode': 0,
                'retMsg': ret_msg,
                'result': f14v2_list_serializer.data,
                'retExtInfo': pagination_list_serializer.data,
                'retTime': int(time.time() * 10 ** 3)
            }
        )
        return_serializer.is_valid()

        return return_serializer


def get_grouped_rule_services(date_from: date, date_to: date) -> list:
    result = list()

    def find_rule_service(services: set) -> int | None:
        for result_idx, result_item in enumerate(result):
            if result_item['services'] == services:
                return result_idx
        return None

    # Get orders settings
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

            # Get order parameters
            order_code = order.get('code', None)
            order_name = order.get('наименование', None)
            order_author = order.get('автор', None)
            order_valid = order.get('действителен', None)
            if order_valid and isinstance(order_valid, dict):
                order_valid_from = order_valid.get('от', None)
                order_valid_to = order_valid.get('до', None)
            else:
                order_valid_from = None
                order_valid_to = None

            # Check type of values of date parameters
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

            # Check order valid dates with report period
            if order_valid_from > date_to:
                continue
            if order_valid_to and isinstance(order_valid_to, date) and order_valid_to < date_from:
                continue

            # Get order rules list
            rules = order.get('правила', None)
            if not rules or not isinstance(rules, list):
                break

            for rule in rules:
                if not isinstance(rule, dict):
                    continue

                # Get rule parameters
                rule_code = rule.get('code', None)
                rule_name = rule.get('наименование', None)
                rule_text = rule.get('текст', None)

                # Get diagnoses templates string
                rule_diagnoses = rule.get('диагнозы', None)
                if not rule_diagnoses or not isinstance(rule_diagnoses, str):
                    continue

                # Get expanded verified by dictionary list of diagnoses
                rule_expanded_diagnoses = expand_diagnoses(rule_diagnoses)

                # Get rule mandatory services list
                rule_mandatory_services = rule.get('обязательныеУслуги', None)
                if not rule_mandatory_services or not isinstance(rule_mandatory_services, list):
                    continue

                for rule_mandatory_service in rule_mandatory_services:
                    if not rule_mandatory_service or not isinstance(rule_mandatory_service, dict):
                        continue

                    # Get mandatory services item parameters
                    rule_services_code = rule_mandatory_service.get('code', None)
                    rule_services_group = rule_mandatory_service.get('группа', None)
                    rule_services_period = rule_mandatory_service.get('срокРабочихДней', None)
                    rule_services_name = rule_mandatory_service.get('наименование', None)

                    # Get mandatory services item services list
                    rule_services = rule_mandatory_service.get('услуги', None)
                    if not rule_services or not isinstance(rule_services, list):
                        continue

                    # Get verified by dictionary list of services
                    rule_expand_services = expand_services(rule_services)

                    if not rule_expand_services:
                        continue

                    # Try to get index of existing result list item with the same list of services
                    idx = find_rule_service(rule_expand_services)
                    if idx is None:
                        result.append(OrderedDict([
                            ('services_group', rule_services_group),
                            ('services_period', rule_services_period),
                            ('services_name', rule_services_name),
                            ('patients_count', OrderedDict([('all', 0)])),
                            ('referrals_count', OrderedDict([('all', 0)])),
                            ('protocols_count', OrderedDict([('all', 0)])),
                            ('services', rule_expand_services),
                            ('diagnoses', rule_expanded_diagnoses),
                            ('codes', {order_code + '|' + rule_code + '|' + rule_services_code}),
                            ('order_rules', [
                                OrderedDict([
                                    ('order_code', order_code),
                                    ('order_name', order_name),
                                    ('order_valid_from', order_valid_from),
                                    ('order_valid_to', order_valid_to),
                                    ('order_author', order_author),
                                    ('rule_code', rule_code),
                                    ('rule_name', rule_name),
                                    ('rule_text', rule_text),
                                    ('rule_diagnoses', rule_diagnoses),
                                    ('rule_services_code', rule_services_code),
                                ])
                            ]),
                            ('order_valid_from', order_valid_from),
                        ]))
                    else:
                        if result[idx]['order_valid_from'] < order_valid_from:
                            result[idx]['order_valid_from'] = order_valid_from
                            result[idx]['services_group'] = order_valid_from
                            result[idx]['services_period'] = order_valid_from
                            result[idx]['services_name'] = order_valid_from
                        result[idx]['diagnoses'] = result[idx]['diagnoses'].union(rule_expanded_diagnoses)
                        result[idx]['codes'] = \
                            result[idx]['codes'].union({order_code + '|' + rule_code + '|' + rule_services_code})
                        result[idx]['order_rules'].append(
                            OrderedDict([
                                ('order_code', order_code),
                                ('order_name', order_name),
                                ('order_valid_from', order_valid_from),
                                ('order_valid_to', order_valid_to),
                                ('order_author', order_author),
                                ('rule_code', rule_code),
                                ('rule_name', rule_name),
                                ('rule_text', rule_text),
                                ('rule_diagnoses', rule_diagnoses),
                                ('rule_services_code', rule_services_code),
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
            item['codes'] = list(item['codes'])
            item.pop('order_valid_from')

        result = sorted(result, key=lambda x: x['services_group'])

    except Exception as e:
        print(str(e))

    return result


def get_report_indicators(result: list, date_from: date, date_to: date) -> dict:
    mo_oids = set()

    for record in result:
        diagnoses = ','.join(["'" + dz['diagnosis_code'] + "'" for dz in record['diagnoses']])

        # Get patients count
        query_body = """
            SELECT
                ptn_mo_oid, COUNT(*) AS patient_count
            FROM
                api_patientdiagnosismilestones
            WHERE
                diagnosis_mkb10 IN (""" + diagnoses + """) AND
                diagnosis_date BETWEEN '""" + date_from.strftime('%Y-%m-%d') + """"' AND '""" + date_to.strftime('%Y-%m-%d') + """'
            GROUP BY
                ptn_mo_oid
        """
        with connection.cursor() as cursor:
            cursor.execute(query_body)
            patients_counts = cursor.fetchall()

        if patients_counts:
            for patients_count in patients_counts:
                mo_oids = mo_oids.union({str(patients_count[0])})
                record['patients_count']['all'] += patients_count[1]
                record['patients_count'].setdefault(str(patients_count[0]), patients_count[1])

        # Get referrals count
        referrals_codes = ','.join(["'" + code + ":нап'" for code in record['codes']])
        query_body = """
            SELECT
                ptn_mo_oid, COUNT(*) AS patient_count
            FROM
                api_patientdiagnosismilestones
            WHERE
                diagnosis_mkb10 IN (""" + diagnoses + """) AND
                diagnosis_date BETWEEN '""" + date_from.strftime('%Y-%m-%d') + """"' AND '""" + date_to.strftime('%Y-%m-%d') + """' AND
                diagnosis_milestones ?| array[""" + referrals_codes + """]
            GROUP BY
                ptn_mo_oid
            """
        with connection.cursor() as cursor:
            cursor.execute(query_body)
            referrals_counts = cursor.fetchall()

        if referrals_counts:
            for referrals_count in referrals_counts:
                mo_oids = mo_oids.union({str(referrals_count[0])})
                record['referrals_count']['all'] += referrals_count[1]
                record['referrals_count'].setdefault(str(referrals_count[0]), referrals_count[1])

        # Get protocols count
        protocols_codes = ','.join(["'" + code + ":исп'" for code in record['codes']])
        query_body = """
            SELECT
                ptn_mo_oid, COUNT(*) AS patient_count
            FROM
                api_patientdiagnosismilestones
            WHERE
                diagnosis_mkb10 IN (""" + diagnoses + """) AND
                diagnosis_date BETWEEN '""" + date_from.strftime('%Y-%m-%d') + """"' AND '""" + date_to.strftime('%Y-%m-%d') + """' AND
                diagnosis_milestones ?| array[""" + protocols_codes + """]
            GROUP BY
                ptn_mo_oid
            """
        with connection.cursor() as cursor:
            cursor.execute(query_body)
            protocols_counts = cursor.fetchall()

        if protocols_counts:
            for protocols_count in protocols_counts:
                mo_oids = mo_oids.union({str(protocols_count[0])})
                record['protocols_count']['all'] += protocols_count[1]
                record['protocols_count'].setdefault(str(protocols_count[0]), protocols_count[1])

    result = OrderedDict([
        ('milestones', result),
        ('medical_organizations', expand_mos(mo_oids)),
    ])

    return result
