from django.db.models import Q
from django_filters import rest_framework as filters

from api.filters.filters import ExtraFilterSet
from api.models.registry_models import DiagnosisRegistry


def filter_diagnosis_registry_q(queryset, name, value):
    return queryset.filter(Q(name__icontains=value) | Q(short_name__icontains=value))


def filter_diagnosis_registry_oncor_tag_rid(queryset, name, value):
    return queryset.filter(oncor_tag_rid=value)


class DiagnosisRegistryFilter(ExtraFilterSet):
    """
        Diagnosis registry filters
    """
    q = \
        filters.CharFilter(label='Diagnosis registry name, short name, diagnosis code and diagnosis name '
                                 'for result set filtering (by content case insensitive).',
                           method=filter_diagnosis_registry_q)
    oncor_tag_rid = \
        filters.CharFilter(label='Diagnosis registry oncor tag @rid for result set filtering.',
                           method=filter_diagnosis_registry_oncor_tag_rid)

    class Meta:
        model = DiagnosisRegistry
        fields = ['oncor_tag_rid']
