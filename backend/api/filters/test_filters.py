from django.db.models import Q
from django_filters import rest_framework as filters

from api.filters.filters import ExtraFilterSet
from api.models.test_models import Company


def filter_company_q(queryset, name, value):
    return queryset.filter(Q(name__icontains=value) | Q(email__icontains=value))


def filter_company_is_active(queryset, name, value):
    return queryset.filter(is_active=value)


def filter_company_is_deleted(queryset, name, value):
    return queryset.filter(is_deleted=value)


class CompanyFilter(ExtraFilterSet):
    """
        Company filters
    """
    q = \
        filters.CharFilter(label='Company name and email for result set filtering (by content case insensitive).',
                           method=filter_company_q)

    is_active = \
        filters.BooleanFilter(label='Is active flag for result set filtering.',
                              method=filter_company_is_active)

    is_deleted = \
        filters.BooleanFilter(label='Is deleted flag for result set filtering.',
                              method=filter_company_is_deleted)

    class Meta:
        model = Company
        fields = ['is_active', 'is_deleted']


