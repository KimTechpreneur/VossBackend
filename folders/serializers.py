from rest_framework import serializers
from .models import (
    Folder, FolderFile, FolderTransfer, FolderService,
    FolderCategory, RetentionClass, FolderSignature,
    FolderWorkflowStep, FolderComment
)

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
    class Meta:
        model = RetentionClass
        fields = ['id', 'name', 'description', 'retention_period', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class FolderFileSerializer(serializers.ModelSerializer):
    formatted_size = serializers.CharField(read_only=True)

    class Meta:
        model = FolderFile
        fields = [
            'id', 'folder', 'file', 'original_filename', 'file_type', 
            'file_size', 'formatted_size', 'uploaded_by', 'uploaded_at',
            'description', 'file_number', 'is_archived', 'archived_at',
            'archived_by', 'is_selected'
        ]
        read_only_fields = ['id', 'uploaded_at', 'archived_at']

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
    service_name = serializers.CharField(source='service.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    retention_class_name = serializers.CharField(source='retention_class.name', read_only=True)
    source_office_name = serializers.CharField(source='source_office.office_name', read_only=True)
    destination_office_name = serializers.CharField(source='destination_office.office_name', read_only=True)
    current_office_name = serializers.CharField(source='current_office.office_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    last_modified_by_name = serializers.CharField(source='last_modified_by.full_name', read_only=True)
    assigned_agent_name = serializers.CharField(source='assigned_agent.full_name', read_only=True)
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
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']

class FolderBulkUpdateSerializer(serializers.Serializer):
    folder_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    status = serializers.ChoiceField(
        choices=Folder.STATUS_CHOICES,
        required=False
    )
    priority = serializers.ChoiceField(
        choices=Folder.PRIORITY_CHOICES,
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