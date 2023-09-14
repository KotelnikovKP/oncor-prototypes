from rest_framework import serializers

from api.serializers.serializers import BaseResponseSerializer, PaginationListSerializer


class ServiceSerializer(serializers.Serializer):
    """
        Standard service schema (for all responses)
    """
    service_code = serializers.CharField(help_text='Medical service code')
    service_name = serializers.CharField(help_text='Medical service name')


class DiagnosisSerializer(serializers.Serializer):
    """
        Standard diagnosis schema (for all responses)
    """
    diagnosis_code = serializers.CharField(help_text='Diagnosis code')
    diagnosis_name = serializers.CharField(help_text='Diagnosis name')


class OrderRuleSerializer(serializers.Serializer):
    """
        Standard order rule schema (for all responses)
    """
    order_name = serializers.CharField(required=False, help_text='Order name')
    order_valid_from = serializers.DateField(required=False, help_text='Order valid from')
    order_valid_to = serializers.DateField(required=False, help_text='Order valid from')
    order_author = serializers.CharField(required=False, help_text='Order author')
    rule_name = serializers.CharField(required=False, help_text='Order rule name')
    rule_text = serializers.CharField(required=False, help_text='Order rule text')
    rule_diagnoses = serializers.CharField(required=False, help_text='Order rule diagnoses template')


class F14Serializer(serializers.Serializer):
    """
        Standard F14 schema (for all responses)
    """
    row_number = serializers.IntegerField(help_text='F14 row number')
    mo_oid = serializers.CharField(required=False, help_text='F14 row medical organization OID')
    mo_name = serializers.CharField(required=False, help_text='F14 row medical organization name')
    services_group = serializers.CharField(help_text='F14 row name of service group')
    services_period = serializers.IntegerField(required=False, help_text='Medical services period')
    services_name = serializers.CharField(required=False, help_text='Medical services name')
    services = ServiceSerializer(many=True)
    patients_count = serializers.IntegerField(required=False, help_text='F14 row count of patients')
    referrals_count = serializers.IntegerField(required=False, help_text='F14 row count of referrals')
    protocols_count = serializers.IntegerField(required=False, help_text='F14 row count of protocols')
    diagnoses = DiagnosisSerializer(many=True)
    order_rules = OrderRuleSerializer(required=False, many=True)


class F14ListSerializer(BaseResponseSerializer):
    """
        Patient list schema
    """
    result = F14Serializer(many=True)
    retExtInfo = PaginationListSerializer()
