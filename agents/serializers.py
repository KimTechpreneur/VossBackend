from rest_framework import serializers
from .models import Agent, AgentDelivery, BaseOffice
from users.serializers import UserSerializer

class BaseOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseOffice
        fields = ['id', 'name']

class AgentDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentDelivery
        fields = [
            'id', 'delivery_id', 'date', 'status', 'from_location', 
            'to_location', 'time_taken', 'confirmation_type', 'exception'
        ]

class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    base_office = BaseOfficeSerializer(read_only=True)
    base_office_id = serializers.UUIDField(write_only=True)
    deliveries_today = serializers.IntegerField(read_only=True)
    success_rate = serializers.IntegerField(read_only=True)
    initials = serializers.CharField(source='user.initials', read_only=True)

    class Meta:
        model = Agent
        fields = [
            'id', 'agent_id', 'user', 'status', 'base_office', 'base_office_id',
            'employment_type', 'joined_date', 'last_activity', 'deliveries_today',
            'success_rate', 'initials', 'notes'
        ]
        read_only_fields = ['agent_id', 'deliveries_today', 'success_rate', 'initials']

    def create(self, validated_data):
        base_office_id = validated_data.pop('base_office_id')
        base_office = BaseOffice.objects.get(id=base_office_id)
        validated_data['base_office'] = base_office
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'base_office_id' in validated_data:
            base_office_id = validated_data.pop('base_office_id')
            base_office = BaseOffice.objects.get(id=base_office_id)
            validated_data['base_office'] = base_office
        return super().update(instance, validated_data)

class AgentListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.full_name')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    base_office = serializers.CharField(source='base_office.name')
    initials = serializers.CharField(source='user.initials')
    deliveries_today = serializers.IntegerField(read_only=True)
    success_rate = serializers.IntegerField(read_only=True)

    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'email', 'phone', 'status', 'base_office',
            'employment_type', 'joined_date', 'last_activity', 'deliveries_today',
            'success_rate', 'initials'
        ]

class AgentDeliveryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentDelivery
        fields = [
            'id', 'delivery_id', 'date', 'status', 'from_location',
            'to_location', 'time_taken', 'confirmation_type'
        ]

class AgentBulkUpdateSerializer(serializers.Serializer):
    agent_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    status = serializers.ChoiceField(
        choices=Agent.STATUS_CHOICES,
        required=False
    )
    vehicle_number = serializers.CharField(required=False, allow_null=True)
    vehicle_type = serializers.CharField(required=False, allow_null=True)
    license_number = serializers.CharField(required=False, allow_null=True)
    license_expiry = serializers.DateField(required=False, allow_null=True)
    insurance_number = serializers.CharField(required=False, allow_null=True)
    insurance_expiry = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True)

    def validate(self, data):
        if len(data) < 2:  # At least one field besides agent_ids
            raise serializers.ValidationError("At least one field to update must be provided")
        return data 