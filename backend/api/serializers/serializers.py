from rest_framework import serializers, status


class SimpleResponseSerializer(serializers.Serializer):
    """
        Error schema
    """
    detail = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


simple_responses = {
    status.HTTP_400_BAD_REQUEST: SimpleResponseSerializer,
    status.HTTP_401_UNAUTHORIZED: SimpleResponseSerializer,
    status.HTTP_403_FORBIDDEN: SimpleResponseSerializer,
    status.HTTP_404_NOT_FOUND: SimpleResponseSerializer,
}


class BaseResponseSerializer(serializers.Serializer):
    """
        Base response schema (all response schema are its children)
    """
    retCode = serializers.IntegerField(help_text='Return code')
    retMsg = serializers.CharField(help_text='Return message')
    result = serializers.CharField(help_text='Result')
    retExtInfo = serializers.CharField(help_text='External result information')
    retTime = serializers.IntegerField(help_text='Return timestamp')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PaginationListSerializer(serializers.Serializer):
    """
        Pagination list's extra information schema
    """
    count_items = serializers.IntegerField(help_text='Total number of items in result set')
    items_per_page = serializers.IntegerField(help_text='Number of items on one page')
    start_item_index = serializers.IntegerField(help_text='Index of start item on current page')
    end_item_index = serializers.IntegerField(help_text='Index of end item on current page')
    previous_page = serializers.IntegerField(help_text='Number of previous page (null if the current page is the last)')
    current_page = serializers.IntegerField(help_text='Number of current page')
    next_page = serializers.IntegerField(help_text='Number of next page (null if the current page is the first)')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
