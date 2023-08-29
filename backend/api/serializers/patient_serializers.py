from rest_framework import serializers

from api.serializers.serializers import BaseResponseSerializer, PaginationListSerializer


class PatientDiagnosisSerializer(serializers.Serializer):
    """
        Standard patient diagnosis schema (for all responses)
    """
    diagnosis_code = serializers.CharField(help_text='Diagnosis mkb10 code')
    diagnosis_name = serializers.CharField(required=False, help_text='Diagnosis name')
    diagnosis_date = serializers.DateField(required=False, help_text='Diagnosis date')


class PatientTagSerializer(serializers.Serializer):
    """
        Standard patient diagnosis schema (for all responses)
    """
    tag_rid = serializers.CharField(help_text='Tag @rid')
    tag_name = serializers.CharField(required=False, help_text='Tag name')
    tag_description = serializers.CharField(required=False, help_text='Tag description')


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
