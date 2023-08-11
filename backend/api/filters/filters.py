from django_filters import rest_framework as filters
from django_filters.fields import RangeField, DateRangeField, DateTimeRangeField, IsoDateTimeRangeField, TimeRangeField
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter


class ExtraFilterSet(filters.FilterSet):
    @classmethod
    def get_api_filters(cls):
        filter_parameters = list()
        for f in dict(cls.get_filters()).values():
            if issubclass(f.field_class, RangeField):
                if f.field_class is DateTimeRangeField or f.field_class is IsoDateTimeRangeField:
                    filter_parameters.append(
                        OpenApiParameter(f.field_name+'_after', OpenApiTypes.DATETIME, OpenApiParameter.QUERY,
                                         description=f.label)
                    )
                    filter_parameters.append(
                        OpenApiParameter(f.field_name+'_before', OpenApiTypes.DATETIME, OpenApiParameter.QUERY,
                                         description=f.label)
                    )
                elif f.field_class is DateRangeField:
                    filter_parameters.append(
                        OpenApiParameter(f.field_name + '_after', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                                         description=f.label)
                    )
                    filter_parameters.append(
                        OpenApiParameter(f.field_name + '_before', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                                         description=f.label)
                    )
                elif f.field_class is TimeRangeField:
                    filter_parameters.append(
                        OpenApiParameter(f.field_name + '_after', OpenApiTypes.TIME, OpenApiParameter.QUERY,
                                         description=f.label)
                    )
                    filter_parameters.append(
                        OpenApiParameter(f.field_name + '_before', OpenApiTypes.TIME, OpenApiParameter.QUERY,
                                         description=f.label)
                    )
                else:
                    filter_parameters.append(
                        OpenApiParameter(f.field_name + '_min', OpenApiTypes.NUMBER, OpenApiParameter.QUERY,
                                         description=f.label)
                    )
                    filter_parameters.append(
                        OpenApiParameter(f.field_name + '_max', OpenApiTypes.NUMBER, OpenApiParameter.QUERY,
                                         description=f.label)
                    )
            else:
                filter_parameters.append(
                    OpenApiParameter(f.field_name, OpenApiTypes.STR, OpenApiParameter.QUERY, description=f.label)
                )
        return filter_parameters
