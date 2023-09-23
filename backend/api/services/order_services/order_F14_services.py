import time
from collections import OrderedDict
from datetime import datetime, date

from django.db import connection
from django.utils import formats, translation
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.models.semd_models import OncorSettings
from api.serializers.order_serializers import F14ListSerializer
from api.serializers.serializers import PaginationListSerializer
from api.utils.directories_utils import expand_diagnoses, expand_services


class GetF14Service:
    @staticmethod
    def execute(request: Request, view: ModelViewSet, *args, **kwargs) -> F14ListSerializer:
        """
            Retrieve orders F14 report
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
        result = get_grouped_rule_services()

        # Get report indicators
        result = get_report_indicators(result, date_from, date_to)

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

        elapsed = time.perf_counter() - s_all

        ret_msg = 'Ok' if count > 0 else 'Result set is empty'
        ret_msg += f", processing time = {elapsed: 0.12f}"

        # Formate response schema
        return_serializer = F14ListSerializer(
            data={
                'retCode': 0,
                'retMsg': ret_msg,
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
        for result_idx, result_item in enumerate(result):
            if result_item['services_group'] == services_group and result_item['services'] == services:
                return result_idx
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

            order_name = order.get('наименование', None)
            order_author = order.get('автор', None)
            order_valid = order.get('действителен', None)
            if order_valid and isinstance(order_valid, dict):
                order_valid_from = order_valid.get('от', None)
                order_valid_to = order_valid.get('до', None)
            else:
                order_valid_from = None
                order_valid_to = None

            rules = order.get('правила', None)
            if not rules or not isinstance(rules, list):
                break

            for rule in rules:
                if not isinstance(rule, dict):
                    continue

                rule_name = rule.get('наименование', None)
                rule_text = rule.get('текст', None)

                rule_diagnoses = rule.get('диагнозы', None)
                if not rule_diagnoses or not isinstance(rule_diagnoses, str):
                    continue

                rule_expanded_diagnoses = expand_diagnoses(rule_diagnoses)

                rule_mandatory_services = rule.get('обязательныеУслуги', None)
                if not rule_mandatory_services or not isinstance(rule_mandatory_services, list):
                    continue

                for rule_mandatory_service in rule_mandatory_services:
                    if not rule_mandatory_service or not isinstance(rule_mandatory_service, dict):
                        continue

                    rule_services_group = rule_mandatory_service.get('группа', None)
                    rule_services_period = rule_mandatory_service.get('срокРабочихДней', None)
                    rule_services_name = rule_mandatory_service.get('наименование', None)
                    rule_services = rule_mandatory_service.get('услуги', None)

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
                            ('diagnoses', rule_expanded_diagnoses),
                            ('order_rules', [
                                OrderedDict([
                                    ('order_name', order_name),
                                    ('order_valid_from', order_valid_from),
                                    ('order_valid_to', order_valid_to),
                                    ('order_author', order_author),
                                    ('rule_name', rule_name),
                                    ('rule_text', rule_text),
                                    ('rule_diagnoses', rule_diagnoses),
                                ])
                            ]),
                        ]))
                    else:
                        result[idx]['diagnoses'] = result[idx]['diagnoses'].union(rule_expanded_diagnoses)
                        result[idx]['order_rules'].append(
                            OrderedDict([
                                ('order_name', order_name),
                                ('order_valid_from', order_valid_from),
                                ('order_valid_to', order_valid_to),
                                ('order_author', order_author),
                                ('rule_name', rule_name),
                                ('rule_text', rule_text),
                                ('rule_diagnoses', rule_diagnoses),
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


def get_report_indicators(result: list, date_from: date, date_to: date) -> list:
    for record in result:
        diagnoses = ','.join(["'" + dz['diagnosis_code'] + "'" for dz in record['diagnoses']])

        # Get patients count
        query_body = """
            SELECT
                COUNT(sd.*) as patient_count
            FROM
                (SELECT
                     ptn_id, MIN(diagnosis_date) AS min_diagnosis_date
                 FROM
                     api_semddiagnosis
                 WHERE
                     diagnosis_mkb10 IN (""" + diagnoses + """)
                 GROUP BY
                     ptn_id) AS sd
            WHERE
                min_diagnosis_date BETWEEN '""" + date_from.strftime('%Y-%m-%d') + """"' AND '""" + date_to.strftime('%Y-%m-%d') + """'
        """
        with connection.cursor() as cursor:
            cursor.execute(query_body)
            patients_count = cursor.fetchall()

        record['patients_count'] = patients_count[0][0] if patients_count and len(patients_count) == 1 else 0

        services = ','.join(["'" + srv['service_code'] + "'" for srv in record['services']])

        # Get referrals count
        query_body = """
            SELECT
                COUNT(sd.*) as referrals_count
            FROM
                (SELECT
                     ssd.ptn_id, ssd.min_diagnosis_date
                 FROM
                     (SELECT
                          ptn_id, MIN(diagnosis_date) AS min_diagnosis_date
                      FROM
                          api_semddiagnosis
                      WHERE
                          diagnosis_mkb10 IN (""" + diagnoses + """)
                      GROUP BY
                          ptn_id) AS ssd
                 WHERE
                     min_diagnosis_date BETWEEN '""" + date_from.strftime('%Y-%m-%d') + """"' AND '""" + date_to.strftime('%Y-%m-%d') + """') AS sd
                LEFT JOIN
                    (SELECT
                         sss.ptn_id, MIN(sss.time_rc) AS min_services_date
                     FROM
                         api_semdservice sss
                     WHERE
                         sss.time_rc > (SELECT
                                            sssd.min_diagnosis_date
                                        FROM
                                            (SELECT
                                                 MIN(diagnosis_date) AS min_diagnosis_date
                                             FROM
                                                 api_semddiagnosis
                                             WHERE
                                                 diagnosis_mkb10 IN (""" + diagnoses + """) AND
                                                 ptn_id = sss.ptn_id) AS sssd
                                        WHERE
                                            sssd.min_diagnosis_date BETWEEN '""" + date_from.strftime('%Y-%m-%d') + """"' AND '""" + date_to.strftime('%Y-%m-%d') + """') AND
                         service_code IN (""" + services + """) AND
                         document_type IN ('1','27')
                     GROUP BY
                         ptn_id) ss ON sd.ptn_id = ss.ptn_id
            WHERE
                ss.min_services_date IS NOT NULL
            """
        with connection.cursor() as cursor:
            cursor.execute(query_body)
            referrals_count = cursor.fetchall()

        record['referrals_count'] = referrals_count[0][0] if referrals_count and len(referrals_count) == 1 else 0

        # Get protocols count
        query_body = """
                SELECT
                    COUNT(sd.*) AS protocols_count
                FROM
                    (SELECT
                         ssd.ptn_id, ssd.min_diagnosis_date
                     FROM
                         (SELECT
                              ptn_id, MIN(diagnosis_date) AS min_diagnosis_date
                          FROM
                              api_semddiagnosis
                          WHERE
                              diagnosis_mkb10 IN (""" + diagnoses + """)
                          GROUP BY
                              ptn_id) AS ssd
                     WHERE
                         min_diagnosis_date BETWEEN '""" + date_from.strftime('%Y-%m-%d') + """"' AND '""" + date_to.strftime('%Y-%m-%d') + """') AS sd
                    LEFT JOIN
                        (SELECT
                             sss.ptn_id, MIN(sss.service_date) AS min_services_date
                         FROM
                             api_semdservice sss
                         WHERE
                             sss.service_date > (SELECT
                                                    sssd.min_diagnosis_date
                                                 FROM
                                                     (SELECT
                                                          MIN(diagnosis_date) AS min_diagnosis_date
                                                      FROM
                                                          api_semddiagnosis
                                                      WHERE
                                                          diagnosis_mkb10 IN (""" + diagnoses + """) AND
                                                          ptn_id = sss.ptn_id) AS sssd
                                                 WHERE
                                                     sssd.min_diagnosis_date BETWEEN '""" + date_from.strftime('%Y-%m-%d') + """"' AND '""" + date_to.strftime('%Y-%m-%d') + """') AND
                             service_code IN (""" + services + """) AND
                             document_type IN ('2','3','4','9','12','20')
                         GROUP BY
                             ptn_id) ss ON sd.ptn_id = ss.ptn_id
                WHERE
                    ss.min_services_date IS NOT NULL;
            """
        with connection.cursor() as cursor:
            cursor.execute(query_body)
            protocols_count = cursor.fetchall()

        record['protocols_count'] = protocols_count[0][0] if protocols_count and len(protocols_count) == 1 else 0

    return result
