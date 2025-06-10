from rest_framework import serializers
from .models import (
    DashboardMetrics, NotificationItem, ActivityItem,
    OverdueUnit, AuditItem, HealthMetric,
    TransferVolumeData, ProcessingTimeData, AgentSuccessData
)

class NotificationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationItem
        fields = [
            'id', 'type', 'title', 'message', 'timestamp',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at', 'updated_at']

class ActivityItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityItem
        fields = [
            'id', 'type', 'title', 'description', 'timestamp',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at', 'updated_at']

class OverdueUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OverdueUnit
        fields = [
            'id', 'name', 'overdue_count', 'avg_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AuditItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditItem
        fields = [
            'id', 'user', 'action', 'timestamp',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at', 'updated_at']

class HealthMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthMetric
        fields = [
            'id', 'title', 'value', 'percentage', 'color',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TransferVolumeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferVolumeData
        fields = ['id', 'labels', 'datasets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProcessingTimeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingTimeData
        fields = ['id', 'labels', 'datasets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AgentSuccessDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentSuccessData
        fields = ['id', 'labels', 'datasets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DashboardMetricsSerializer(serializers.ModelSerializer):
    notifications = NotificationItemSerializer(many=True, read_only=True)
    activities = ActivityItemSerializer(many=True, read_only=True)
    overdue_units = OverdueUnitSerializer(many=True, read_only=True)
    audit_items = AuditItemSerializer(many=True, read_only=True)
    health_metrics = HealthMetricSerializer(many=True, read_only=True)
    transfer_volume = TransferVolumeDataSerializer(read_only=True)
    processing_time = ProcessingTimeDataSerializer(read_only=True)
    agent_success = AgentSuccessDataSerializer(read_only=True)

    class Meta:
        model = DashboardMetrics
        fields = [
            'id', 'total_active_transfers', 'pending_approvals',
            'overdue_transfers', 'agent_performance', 'notifications',
            'activities', 'overdue_units', 'audit_items',
            'health_metrics', 'transfer_volume', 'processing_time',
            'agent_success', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 