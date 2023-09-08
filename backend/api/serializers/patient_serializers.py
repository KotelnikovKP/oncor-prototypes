from rest_framework import serializers

from api.serializers.serializers import BaseResponseSerializer, PaginationListSerializer


class SemdCodeNodeSerializer(serializers.Serializer):
    """
        Standard SEMD "code" node schema (for all responses)
    """
    code = serializers.CharField(required=False, help_text='SEMD "code" node code')
    display_name = serializers.CharField(required=False, help_text='SEMD "code" node displayName')
    code_system = serializers.CharField(required=False, help_text='SEMD "code" node codeSystem')
    code_system_version = serializers.CharField(required=False, help_text='SEMD "code" node codeSystemVersion')
    code_system_name = serializers.CharField(required=False, help_text='SEMD "code" node codeSystemName')


class SemdDiagnosisSerializer(serializers.Serializer):
    """
        Standard SEMD one item of diagnosis schema (for all responses)
    """
    date = serializers.DateField(required=False, help_text='SEMD diagnosis set date')
    document_type = serializers.CharField(required=False, help_text='SEMD document_type')
    internal_message_id = serializers.CharField(required=False, help_text='SEMD internal_message_id')
    internal_message_time = serializers.DateField(required=False, help_text='SEMD effectiveTime')
    parent_node_name = serializers.CharField(required=False, help_text='SEMD name of parent of diagnoses node')
    parent_node_class_code = serializers.CharField(required=False,
                                                   help_text='SEMD classCode of parent of diagnoses node')
    parent_node_code_node = SemdCodeNodeSerializer(many=False, required=False)
    code_node = SemdCodeNodeSerializer(many=False, required=False)


class PatientDiagnosisSerializer(serializers.Serializer):
    """
        Standard patient diagnosis schema (for all responses)
    """
    diagnosis_code = serializers.CharField(help_text='Diagnosis mkb10 code')
    diagnosis_name = serializers.CharField(required=False, help_text='Diagnosis name')
    diagnosis_first_date = serializers.DateField(required=False, help_text='Diagnosis first date')
    diagnosis_first_kind_code = serializers.CharField(required=False, help_text='Diagnosis first kind code')
    diagnosis_first_kind_name = serializers.CharField(required=False, help_text='Diagnosis first kind name')
    diagnoses_in_semds = SemdDiagnosisSerializer(many=True, required=False)


class PatientTagSerializer(serializers.Serializer):
    """
        Standard patient diagnosis schema (for all responses)
    """
    tag_rid = serializers.CharField(help_text='Tag @rid')
    tag_name = serializers.CharField(required=False, help_text='Tag name')
    tag_description = serializers.CharField(required=False, help_text='Tag description')


class PatientAddress(serializers.Serializer):
    """
        Standard patient address schema (for all responses)
    """
    locality_type = serializers.CharField(required=False, help_text='Locality type')
    locality_name = serializers.CharField(required=False, help_text='Locality name')
    address = serializers.CharField(help_text='Locality address')


class PatientSerializer(serializers.Serializer):
    """
        Standard patient schema (for all responses)
    """
    rid = serializers.CharField(help_text='Patient @rid')
    lastname = serializers.CharField(help_text='Patient last name')
    firstname = serializers.CharField(help_text='Patient first name')
    middlename = serializers.CharField(help_text='Patient middle name')
    birthday = serializers.DateField(help_text='Patient birthday')
    gender = serializers.CharField(help_text='Patient gender')
    snils = serializers.CharField(help_text='Patient SNILS')
    mo_oid = serializers.CharField(help_text='Patient assigned clinic oid')
    mo_name = serializers.CharField(help_text='Patient assigned clinic name')
    med_terr = serializers.CharField(help_text='Patient medical territory')
    living_area_type = serializers.CharField(help_text='Patient living area type')
    phones = serializers.CharField(help_text='Patient phones')
    address = PatientAddress(many=False)
    base_diagnoses = PatientDiagnosisSerializer(many=True)
    semd_diagnoses = PatientDiagnosisSerializer(many=True)
    tags = PatientTagSerializer(many=True)

    # class Meta:
    #     model = Patient
    #     fields = ('snils', 'name', 'gender', 'birthday', 'diagnoses', 'medical_cards')


class PatientListSerializer(BaseResponseSerializer):
    """
        Patient list schema
    """
    result = PatientSerializer(many=True)
    retExtInfo = PaginationListSerializer()


class PatientDetailsSerializer(BaseResponseSerializer):
    """
        Patient details schema
    """
    result = PatientSerializer(many=False)


class PatientListDiagnosisSerializer(BaseResponseSerializer):
    """
        Patient diagnosis list schema
    """
    result = PatientDiagnosisSerializer(many=True)
    retExtInfo = PaginationListSerializer()


# class PatientRegistryReportSerializer(serializers.Serializer):
#     """
#         Patient Registry report schema
#     """
#     events = SEMDSerializer(many=True, read_only=True)
#     medical_tests = SemdTestSerializer(many=True, read_only=True)
#     medical_examinations = SEMDSerializer(many=True, read_only=True)
#     treatment = SEMDSerializer(many=True, read_only=True)
#     recommended_therapy = SEMDSerializer(many=True, read_only=True)
#
#     def create(self, validated_data):
#         pass
#
#     def update(self, instance, validated_data):
#         pass
#
#
# class PatientRegistryReportDetailSerializer(BaseResponseSerializer):
#     """
#         Patient Registry report details schema
#     """
#     result = PatientRegistryReportSerializer()
