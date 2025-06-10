from rest_framework import serializers
from .models import (
    SearchResultItem, SearchFilters, TransferPathStep,
    AgentActivity, TransferTrail, SearchHistory, SearchResult
)

class TransferPathStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferPathStep
        fields = [
            'id', 'folder', 'office', 'status', 'timestamp',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at', 'updated_at']

class AgentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentActivity
        fields = [
            'id', 'transfer', 'agent', 'status', 'timestamp',
            'location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at', 'updated_at']

class TransferTrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferTrail
        fields = [
            'id', 'folder', 'current_position',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SearchFiltersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchFilters
        fields = [
            'id', 'search_term', 'date_from', 'date_to',
            'destination_unit', 'office', 'file_type',
            'current_status', 'agent', 'treatment_folder_id',
            'specific_file_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SearchResultItemSerializer(serializers.ModelSerializer):
    folder = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    current_office = serializers.SerializerMethodField()

    class Meta:
        model = SearchResultItem
        fields = [
            'id', 'folder', 'file', 'current_office',
            'current_status', 'last_activity', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'last_activity', 'created_at', 'updated_at'
        ]

    def get_folder(self, obj):
        from folders.serializers import FolderSerializer
        return FolderSerializer(obj.folder).data

    def get_file(self, obj):
        if obj.file:
            from folders.serializers import FolderFileSerializer
            return FolderFileSerializer(obj.file).data
        return None

    def get_current_office(self, obj):
        if obj.current_office:
            from offices.serializers import InternalOfficeSerializer
            return InternalOfficeSerializer(obj.current_office).data
        return None

class SearchBulkUpdateSerializer(serializers.Serializer):
    search_result_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    current_status = serializers.ChoiceField(
        choices=SearchResultItem.STATUS_CHOICES,
        required=False
    )
    current_office = serializers.PrimaryKeyRelatedField(
        queryset='offices.InternalOffice.objects.all()',
        required=False
    )

    def validate(self, data):
        if not any([data.get('current_status'), data.get('current_office')]):
            raise serializers.ValidationError(
                "At least one of current_status or current_office must be provided"
            )
        return data

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = [
            'id', 'user', 'search_term', 'filters',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class SearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchResult
        fields = [
            'id', 'search_history', 'result_type',
            'result_id', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 