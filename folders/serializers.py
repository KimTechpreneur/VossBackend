from rest_framework import serializers, fields
from .models import (
    Folder, FolderFile, FolderTransfer, FolderService,
    FolderCategory, RetentionClass, FolderSignature,
    FolderWorkflowStep, FolderComment
)
from isodate import parse_duration, duration_isoformat
from datetime import timedelta

class CustomDurationField(fields.Field):
    """
    A custom field to handle ISO 8601 duration strings and 'PERMANENT'.
    """
    def to_representation(self, value):
        if value == timedelta(days=36500):  # Magic number for permanent
            return 'PERMANENT'
        return duration_isoformat(value)

    def to_internal_value(self, data):
        if str(data).upper() == 'PERMANENT':
            return timedelta(days=36500)
        try:
            return parse_duration(data)
        except Exception:
            raise serializers.ValidationError("Invalid duration format. Use ISO 8601 (e.g., 'P1Y') or 'PERMANENT'.")

class FolderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderService
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class FolderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RetentionClassSerializer(serializers.ModelSerializer):
    retention_period = CustomDurationField()

    class Meta:
        model = RetentionClass
        fields = ['id', 'name', 'description', 'retention_period', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        retention_period_str = validated_data.pop('retention_period')
        if retention_period_str.upper() == 'PERMANENT':
            # Handle "permanent" as a very long time, or a special state
            # For simplicity, let's set it to 9999 days
            validated_data['retention_period'] = '9999-01-01'
        else:
            validated_data['retention_period'] = parse_duration(retention_period_str)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        retention_period_str = validated_data.pop('retention_period', None)
        if retention_period_str:
            if retention_period_str.upper() == 'PERMANENT':
                validated_data['retention_period'] = '9999-01-01'
            else:
                instance.retention_period = parse_duration(retention_period_str)

        return super().update(instance, validated_data)

class FolderFileSerializer(serializers.ModelSerializer):
    formatted_size = serializers.CharField(read_only=True)

    class Meta:
        model = FolderFile
        fields = [
            'id', 'folder', 'file', 'original_filename', 'file_type', 
            'file_size', 'formatted_size', 'uploaded_by', 'uploaded_at',
            'description', 'is_archived', 'archived_at',
            'archived_by'
        ]
        read_only_fields = [
            'id', 'uploaded_at', 'archived_at', 'original_filename', 
            'file_type', 'file_size', 'formatted_size', 'uploaded_by'
        ]

class FolderSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderSignature
        fields = [
            'id', 'folder', 'signed_by', 'signature_type', 'signature_data',
            'signed_at', 'notes', 'is_verified', 'verified_at', 'verified_by'
        ]
        read_only_fields = ['id', 'signed_at', 'verified_at']

class FolderWorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderWorkflowStep
        fields = [
            'id', 'folder', 'office', 'step_number', 'total_steps',
            'status', 'completed_at', 'notes', 'is_required',
            'estimated_duration', 'actual_duration', 'responsible_user',
            'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'completed_at', 'created_at', 'updated_at']

class FolderCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderComment
        fields = [
            'id', 'folder', 'user', 'comment', 'created_at',
            'updated_at', 'is_internal', 'parent_comment'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class FolderTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderTransfer
        fields = [
            'id', 'folder', 'from_office', 'to_office', 'agent',
            'status', 'transfer_date', 'delivered_at', 'notes',
            'confirmation_type', 'time_taken', 'created_by',
            'received_by', 'delivery_method', 'agent_notes',
            'priority', 'tags', 'notifications', 'submitted_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'delivered_at', 'time_taken', 'submitted_at',
            'created_at', 'updated_at'
        ]

class FolderSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True, allow_null=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    retention_class_name = serializers.CharField(source='retention_class.name', read_only=True, allow_null=True)
    source_office_name = serializers.CharField(source='source_office.name', read_only=True, allow_null=True)
    destination_office_name = serializers.CharField(source='destination_office.name', read_only=True, allow_null=True)
    current_office_name = serializers.CharField(source='current_office.name', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    last_modified_by_name = serializers.CharField(source='last_modified_by.get_full_name', read_only=True, allow_null=True)
    assigned_agent_name = serializers.CharField(source='assigned_agent.get_full_name', read_only=True, allow_null=True)
    is_overdue = serializers.BooleanField(read_only=True)
    file_count = serializers.IntegerField(read_only=True)
    current_location = serializers.CharField(read_only=True)
    status_flags = serializers.JSONField(read_only=True)

    class Meta:
        model = Folder
        fields = [
            'id', 'folder_id', 'title', 'subject', 'description', 'status',
            'priority', 'service', 'service_name', 'category', 'category_name',
            'retention_class', 'retention_class_name', 'source_office',
            'source_office_name', 'destination_office', 'destination_office_name',
            'created_by', 'created_by_name', 'assigned_agent', 'assigned_agent_name',
            'requires_signature', 'is_signed', 'forwarding_comment', 'created_at',
            'updated_at', 'due_date', 'completed_at', 'current_office',
            'current_office_name', 'last_modified_by', 'last_modified_by_name',
            'auto_generate_file_numbers', 'tags', 'notifications', 'is_overdue',
            'file_count', 'current_location', 'status_flags'
        ]
        read_only_fields = ['id', 'folder_id', 'created_at', 'updated_at', 'completed_at']

class FolderBulkUpdateSerializer(serializers.Serializer):
    folder_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    status = serializers.ChoiceField(
        choices=Folder.Status.choices,
        required=False
    )
    priority = serializers.ChoiceField(
        choices=Folder.Priority.choices,
        required=False
    )
    assigned_agent = serializers.PrimaryKeyRelatedField(
        queryset='agents.Agent.objects.all()',
        required=False
    )

    def validate(self, data):
        if not any([data.get('status'), data.get('priority'), data.get('assigned_agent')]):
            raise serializers.ValidationError(
                "At least one of status, priority, or assigned_agent must be provided"
            )
        return data

class FolderDetailSerializer(FolderSerializer):
    files = FolderFileSerializer(many=True, read_only=True)
    signatures = FolderSignatureSerializer(many=True, read_only=True)
    workflow_steps = FolderWorkflowStepSerializer(many=True, read_only=True)
    comments = FolderCommentSerializer(many=True, read_only=True)
    transfers = FolderTransferSerializer(many=True, read_only=True)

    class Meta(FolderSerializer.Meta):
        fields = FolderSerializer.Meta.fields + ['files', 'signatures', 'workflow_steps', 'comments', 'transfers'] 