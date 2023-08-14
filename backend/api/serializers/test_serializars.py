from rest_framework import serializers

from api.models.test_models import Company, OFriends, OWorksAt
from api.serializers.serializers import BaseResponseSerializer, PaginationListSerializer


class CompanySerializer(serializers.ModelSerializer):
    """
        Standard company schema (for all responses)
    """
    class Meta:
        model = Company
        fields = ('id', 'name', 'email', 'is_active', 'is_deleted')
        read_only_fields = ('id', )


class CompanyListSerializer(BaseResponseSerializer):
    """
        Company list response schema
    """
    result = CompanySerializer(many=True)
    retExtInfo = PaginationListSerializer()


class CompanySingleEntrySerializer(BaseResponseSerializer):
    """
        Company single entry response schema
    """
    result = CompanySerializer(many=False)


class OFriendsSerializer(serializers.Serializer):
    from_postgresql_ouser_id = serializers.IntegerField()
    to_postgresql_ouser_id = serializers.IntegerField()

    def create(self, data):
        return OFriends.objects.create(**data)

    def update(self, instance, data):
        instance.from_postgresql_ouser_id = data.get("from_postgresql_ouser_id")
        instance.to_postgresql_ouser_id = data.get("to_postgresql_ouser_id")
        instance.save()
        return instance


class OFriendsListSerializer(BaseResponseSerializer):
    """
        OFriends list response schema
    """
    result = OFriendsSerializer(many=True)
    retExtInfo = PaginationListSerializer()


class OFriendsSingleEntrySerializer(BaseResponseSerializer):
    """
        OFriends single entry response schema
    """
    result = OFriendsSerializer(many=False)


class OWorksAtSerializer(serializers.Serializer):
    from_postgresql_ouser_id = serializers.IntegerField()
    to_postgresql_ocompany_id = serializers.IntegerField()

    def create(self, data):
        return OWorksAt.objects.create(**data)

    def update(self, instance, data):
        instance.from_postgresql_ouser_id = data.get("from_postgresql_ouser_id")
        instance.to_postgresql_ocompany_id = data.get("to_postgresql_ocompany_id")
        instance.save()
        return instance


class OWorksAtListSerializer(BaseResponseSerializer):
    """
        OWorksAt list response schema
    """
    result = OWorksAtSerializer(many=True)
    retExtInfo = PaginationListSerializer()


class OWorksAtSingleEntrySerializer(BaseResponseSerializer):
    """
        OWorksAt single entry response schema
    """
    result = OWorksAtSerializer(many=False)


