from rest_framework import serializers

from api.models.registry_models import DiagnosisRegistry
from api.serializers.serializers import BaseResponseSerializer, PaginationListSerializer


class DiagnosisRegistrySerializer(serializers.ModelSerializer):
    """
        Standard diagnosis registry schema
    """

    class Meta:
        model = DiagnosisRegistry
        fields = ('id', 'name', 'short_name', 'oncor_tag_rid', 'medical_record_transcript_settings')
        read_only_fields = ('id', )


class DiagnosisRegistryListSerializer(BaseResponseSerializer):
    """
        Diagnosis registry list response schema
    """
    result = DiagnosisRegistrySerializer(many=True)
    retExtInfo = PaginationListSerializer()


class DiagnosisRegistrySingleEntrySerializer(BaseResponseSerializer):
    """
        Diagnosis registry single entry response schema
    """
    result = DiagnosisRegistrySerializer(many=False)

