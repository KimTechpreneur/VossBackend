from rest_framework import serializers
from .models import Agent, AgentDelivery
from offices.models import Office
from users.serializers import UserSerializer
from users.models import User, Role

class AgentDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentDelivery
        fields = [
            'id', 'delivery_id', 'date', 'status', 'from_location', 
            'to_location', 'time_taken', 'confirmation_type', 'exception'
        ]

class HybridAgentListSerializer(serializers.Serializer):
    """
    Serializer for displaying both full agents and potential agents (users with agent role)
    """
    id = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(allow_null=True, allow_blank=True)
    status = serializers.CharField()
    base_office = serializers.CharField(allow_null=True, allow_blank=True)
    employment_type = serializers.CharField(allow_null=True, allow_blank=True)
    joined_date = serializers.DateTimeField()
    last_activity = serializers.DateTimeField(allow_null=True)
    deliveries_today = serializers.IntegerField()
    success_rate = serializers.IntegerField()
    initials = serializers.CharField()
    has_agent_profile = serializers.BooleanField()
    user_id = serializers.CharField()

class AgentUpgradeSerializer(serializers.Serializer):
    """
    Serializer for upgrading a user to a full agent
    """
    user_id = serializers.UUIDField()
    base_office_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=Agent.STATUS_CHOICES, default='available')
    employment_type = serializers.ChoiceField(choices=Agent.EMPLOYMENT_TYPE_CHOICES, default='Full Time')
    notes = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user_id = validated_data['user_id']
        base_office_id = validated_data['base_office_id']
        
        try:
            user = User.objects.get(id=user_id)
            base_office = Office.objects.get(id=base_office_id)
            
            # Check if user already has an agent profile
            if hasattr(user, 'agent'):
                raise serializers.ValidationError("User already has an agent profile")
            
            # Create the agent profile
            agent = Agent.objects.create(
                user=user,
                base_office=base_office,
                status=validated_data.get('status', 'available'),
                employment_type=validated_data.get('employment_type', 'Full Time'),
                notes=validated_data.get('notes', '')
            )
            
            # Ensure user has Agent role
            try:
                agent_role = Role.objects.get(name='Agent')
                if user.role != agent_role:
                    user.role = agent_role
                    user.save()
            except Role.DoesNotExist:
                pass
            
            return agent
            
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        except Office.DoesNotExist:
            raise serializers.ValidationError("Office not found")

class AgentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an agent. It handles creating a User and an Agent profile.
    """
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    base_office_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Agent
        fields = [
            'email', 'first_name', 'last_name', 'password', 'base_office_id',
            'status', 'employment_type', 'notes'
        ]

    def create(self, validated_data):
        # 1. Create the User
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        
        # 2. Assign the 'Agent' role
        try:
            agent_role = Role.objects.get(name='Agent')
            user.role = agent_role
            user.save()
        except Role.DoesNotExist:
            # Handle case where 'Agent' role doesn't exist.
            # For now, we can log a warning. In a real app, you might want to create it.
            print("Warning: 'Agent' role not found. User was created without it.")
            pass

        # 3. Create the Agent profile
        base_office = Office.objects.get(id=validated_data['base_office_id'])
        
        agent = Agent.objects.create(
            user=user,
            base_office=base_office,
            status=validated_data.get('status', 'available'),
            employment_type=validated_data.get('employment_type', 'Full Time'),
            notes=validated_data.get('notes')
        )
        
        return agent

class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    base_office = serializers.StringRelatedField()
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

    def update(self, instance, validated_data):
        if 'base_office_id' in validated_data:
            base_office_id = validated_data.pop('base_office_id')
            base_office = Office.objects.get(id=base_office_id)
            validated_data['base_office'] = base_office
        
        # Handle user data update if necessary
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()

        return super().update(instance, validated_data)

class AgentListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.first_name')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    base_office = serializers.CharField(source='base_office.office_name')
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