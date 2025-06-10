from rest_framework import serializers
from .models import Report, ReportTemplate

class ReportTemplateSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'query', 'parameters',
            'created_by', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class ReportSerializer(serializers.ModelSerializer):
    template = ReportTemplateSerializer(read_only=True)
    template_id = serializers.PrimaryKeyRelatedField(
        queryset=ReportTemplate.objects.filter(is_active=True),
        source='template',
        write_only=True
    )
    created_by = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'template', 'template_id', 'name', 'parameters',
            'status', 'status_display', 'result', 'file',
            'created_by', 'created_at', 'completed_at', 'error_message'
        ]
        read_only_fields = [
            'created_by', 'created_at', 'completed_at',
            'status', 'result', 'file', 'error_message'
        ] 