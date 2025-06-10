from rest_framework import serializers
from .models import Unit
from users.models import User

class HeadOfUnitOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": f"{instance.first_name} {instance.last_name}".strip()
        }

class UnitSerializer(serializers.ModelSerializer):
    headOfUnit = HeadOfUnitOptionSerializer(source='head_of_unit', read_only=True)
    headOfUnitId = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='head_of_unit', write_only=True, required=False
    )

    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'unit_type', 'unit_code', 'headOfUnit', 'headOfUnitId',
            'location', 'status', 'staff_count', 'ongoing_transfers', 'description'
        ]
        read_only_fields = ['id', 'staff_count', 'ongoing_transfers', 'headOfUnit']

class UnitListItemSerializer(serializers.ModelSerializer):
    headOfUnit = HeadOfUnitOptionSerializer(source='head_of_unit', read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'unit_type', 'unit_code', 'headOfUnit',
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