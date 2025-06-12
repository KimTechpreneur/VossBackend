from rest_framework import serializers
from django.utils import timezone
from .models import Transfer, RoutingStep

class RoutingStepSerializer(serializers.ModelSerializer):
    unit_office = serializers.SerializerMethodField()
    responsible_user = serializers.SerializerMethodField()
    completed_by = serializers.SerializerMethodField()

    class Meta:
        model = RoutingStep
        fields = [
            'id', 'step_number', 'unit_office', 'responsible_user',
            'due_date', 'status', 'notes', 'completed_at', 'completed_by'
        ]
        read_only_fields = ['id', 'completed_at', 'completed_by']

    def get_unit_office(self, obj):
        from offices.serializers import OfficeSerializer
        return OfficeSerializer(obj.unit_office).data

    def get_responsible_user(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.responsible_user).data

    def get_completed_by(self, obj):
        if obj.completed_by:
            from users.serializers import UserSerializer
            return UserSerializer(obj.completed_by).data
        return None

class TransferSerializer(serializers.ModelSerializer):
    folder = serializers.SerializerMethodField()
    source_office = serializers.SerializerMethodField()
    destination_office = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    returned_by = serializers.SerializerMethodField()
    routing_steps = RoutingStepSerializer(many=True, read_only=True)
    current_step = serializers.SerializerMethodField()
    next_step = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = [
            'id', 'folder', 'source_office', 'destination_office',
            'delivery_method', 'agent', 'agent_notes', 'priority',
            'tags', 'notifications', 'status', 'created_at',
            'created_by', 'submitted_at', 'completed_at', 'due_date',
            'return_reason', 'return_notes', 'returned_at', 'returned_by',
            'routing_steps', 'current_step', 'next_step', 'is_overdue',
            'history'
        ]
        read_only_fields = [
            'id', 'created_at', 'created_by', 'submitted_at',
            'completed_at', 'returned_at', 'returned_by', 'history'
        ]

    def get_folder(self, obj):
        from folders.serializers import FolderSerializer
        return FolderSerializer(obj.folder).data

    def get_source_office(self, obj):
        from offices.serializers import OfficeSerializer
        return OfficeSerializer(obj.source_office).data

    def get_destination_office(self, obj):
        from offices.serializers import OfficeSerializer
        return OfficeSerializer(obj.destination_office).data

    def get_agent(self, obj):
        if obj.agent:
            from users.serializers import UserSerializer
            return UserSerializer(obj.agent).data
        return None

    def get_created_by(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.created_by).data

    def get_returned_by(self, obj):
        if obj.returned_by:
            from users.serializers import UserSerializer
            return UserSerializer(obj.returned_by).data
        return None

    def get_current_step(self, obj):
        current = obj.current_step
        return RoutingStepSerializer(current).data if current else None

    def get_next_step(self, obj):
        next_step = obj.next_step
        return RoutingStepSerializer(next_step).data if next_step else None

    def get_is_overdue(self, obj):
        return obj.is_overdue

    def validate(self, data):
        # Validate delivery method and agent
        if data.get('delivery_method') == 'agent' and not data.get('agent'):
            raise serializers.ValidationError(
                "Agent must be specified when delivery method is 'agent'"
            )

        # Validate due date
        due_date = data.get('due_date')
        if due_date and due_date < timezone.now():
            raise serializers.ValidationError(
                "Due date cannot be in the past"
            )

        return data

class CreateTransferSerializer(serializers.ModelSerializer):
    folder_option = serializers.ChoiceField(choices=['create', 'existing'], write_only=True)
    folder_data = serializers.JSONField(write_only=True, required=False)
    existing_folder_id = serializers.CharField(write_only=True, required=False)
    routing_steps = serializers.ListField(write_only=True)
    attached_file_ids = serializers.ListField(write_only=True, required=False)
    source_office_id = serializers.CharField(write_only=True)
    destination_office_id = serializers.CharField(write_only=True)

    class Meta:
        model = Transfer
        fields = [
            'folder_option', 'folder_data', 'existing_folder_id',
            'attached_file_ids', 'routing_steps', 'delivery_method',
            'agent', 'agent_notes', 'priority', 'tags', 'notifications',
            'source_office_id', 'destination_office_id'
        ]

    def validate(self, data):
        folder_option = data.get('folder_option')
        
        if folder_option == 'create':
            if not data.get('folder_data'):
                raise serializers.ValidationError(
                    "folder_data is required when folder_option is 'create'"
                )
        elif folder_option == 'existing':
            if not data.get('existing_folder_id'):
                raise serializers.ValidationError(
                    "existing_folder_id is required when folder_option is 'existing'"
                )
        
        # Validate routing steps
        routing_steps = data.get('routing_steps', [])
        if not routing_steps:
            raise serializers.ValidationError(
                "At least one routing step is required"
            )

        return data

    def create(self, validated_data):
        # Handle folder creation/linking
        folder_option = validated_data.pop('folder_option')
        folder_data = validated_data.pop('folder_data', None)
        existing_folder_id = validated_data.pop('existing_folder_id', None)
        routing_steps_data = validated_data.pop('routing_steps', [])
        attached_file_ids = validated_data.pop('attached_file_ids', [])
        source_office_id = validated_data.pop('source_office_id')
        destination_office_id = validated_data.pop('destination_office_id')

        if folder_option == 'create':
            from folders.serializers import FolderSerializer
            folder_serializer = FolderSerializer(data=folder_data)
            folder_serializer.is_valid(raise_exception=True)
            folder = folder_serializer.save()
        else:
            from folders.models import Folder
            folder = Folder.objects.get(id=existing_folder_id)

        # Create transfer
        transfer = Transfer.objects.create(
            folder=folder,
            created_by=self.context['request'].user,
            source_office_id=source_office_id,
            destination_office_id=destination_office_id,
            **validated_data
        )

        # Create routing steps
        for step_data in routing_steps_data:
            RoutingStep.objects.create(
                transfer=transfer,
                **step_data
            )

        # Handle attached files
        if attached_file_ids:
            from folders.models import FolderFile
            # This logic assumes attached_file_ids refer to a temporary file store
            # and that we can retrieve file metadata from there.
            # This part needs to be adapted to the actual file handling implementation.
            for file_id in attached_file_ids:
                # Placeholder for getting file data from a temporary storage
                # file_obj = TemporaryFile.objects.get(id=file_id)
                FolderFile.objects.create(
                    folder=folder,
                    # file=file_obj.file,
                    # original_filename=file_obj.filename,
                    # file_size=file_obj.size,
                    # file_type=file_obj.content_type,
                    uploaded_by=self.context['request'].user
                )
                # file_obj.delete() # Clean up temporary file

        return transfer

class BulkActionSerializer(serializers.Serializer):
    transfer_ids = serializers.ListField(
        child=serializers.CharField(),
        min_length=1
    )

class ReassignAgentSerializer(serializers.Serializer):
    new_agent_id = serializers.CharField()
    agent_notes = serializers.CharField(required=False, allow_blank=True)

class ReturnRejectSerializer(serializers.Serializer):
    reason = serializers.CharField()
    comments = serializers.CharField(required=False, allow_blank=True)

class RevisionRequestSerializer(serializers.Serializer):
    comments = serializers.CharField() 