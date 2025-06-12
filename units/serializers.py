from rest_framework import serializers
from .models import Unit
from users.models import User
from users.serializers import UserSerializer

class UnitSerializer(serializers.ModelSerializer):
    head_of_unit = UserSerializer(read_only=True)
    head_of_unit_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='head_of_unit', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'unit_type', 'unit_code', 'head_of_unit', 'head_of_unit_id',
            'location', 'status', 'staff_count', 'ongoing_transfers', 'description'
        ]
        read_only_fields = ['id', 'staff_count', 'ongoing_transfers', 'head_of_unit']

class UnitListItemSerializer(serializers.ModelSerializer):
    head_of_unit = UserSerializer(read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'unit_type', 'unit_code', 'head_of_unit',
            'location', 'status', 'staff_count', 'ongoing_transfers', 'description'
        ]

class UnitListSerializer(serializers.Serializer):
    items = UnitListItemSerializer(many=True)
    totalItems = serializers.IntegerField()
    currentPage = serializers.IntegerField()
    totalPages = serializers.IntegerField()
    filters = serializers.DictField()
    sortColumn = serializers.CharField(required=False)
    sortDirection = serializers.CharField(required=False)

class UnitStatusOptionSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()

class UnitTypeOptionSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()

class HeadOfUnitOptionSerializer(serializers.Serializer):
    id = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    
    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
        } 