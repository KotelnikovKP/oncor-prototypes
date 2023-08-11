from rest_framework import pagination


class SemdPageNumberPagination(pagination.PageNumberPagination):
    def get_paginated_response_schema(self, schema):
        return schema['items']
