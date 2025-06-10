from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    DashboardMetrics, NotificationItem, ActivityItem,
    OverdueUnit, AuditItem, HealthMetric,
    TransferVolumeData, ProcessingTimeData, AgentSuccessData
)
from .serializers import (
    DashboardMetricsSerializer, NotificationItemSerializer,
    ActivityItemSerializer, OverdueUnitSerializer,
    AuditItemSerializer, HealthMetricSerializer,
    TransferVolumeDataSerializer, ProcessingTimeDataSerializer,
    AgentSuccessDataSerializer
)
from users.permissions import IsAdminUser

# Create your views here.

class NotificationItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notification items.
    
    list:
    Return a list of all notification items.
    
    create:
    Create a new notification item.
    
    retrieve:
    Return the details of a specific notification item.
    
    update:
    Update all fields of a specific notification item.
    
    partial_update:
    Update one or more fields of a specific notification item.
    
    destroy:
    Delete a specific notification item.
    """
    queryset = NotificationItem.objects.all()
    serializer_class = NotificationItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        notification_type = self.request.query_params.get('notification_type', None)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
            
        return queryset.order_by('-timestamp')

class ActivityItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing activity items.
    
    list:
    Return a list of all activity items.
    
    create:
    Create a new activity item.
    
    retrieve:
    Return the details of a specific activity item.
    
    update:
    Update all fields of a specific activity item.
    
    partial_update:
    Update one or more fields of a specific activity item.
    
    destroy:
    Delete a specific activity item.
    """
    queryset = ActivityItem.objects.all()
    serializer_class = ActivityItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        activity_type = self.request.query_params.get('activity_type', None)
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
            
        return queryset.order_by('-timestamp')

class OverdueUnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing overdue units.
    
    list:
    Return a list of all overdue units.
    
    create:
    Create a new overdue unit.
    
    retrieve:
    Return the details of a specific overdue unit.
    
    update:
    Update all fields of a specific overdue unit.
    
    partial_update:
    Update one or more fields of a specific overdue unit.
    
    destroy:
    Delete a specific overdue unit.
    """
    queryset = OverdueUnit.objects.all()
    serializer_class = OverdueUnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().order_by('-overdue_count')

class AuditItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing audit items.
    
    list:
    Return a list of all audit items.
    
    create:
    Create a new audit item.
    
    retrieve:
    Return the details of a specific audit item.
    
    update:
    Update all fields of a specific audit item.
    
    partial_update:
    Update one or more fields of a specific audit item.
    
    destroy:
    Delete a specific audit item.
    """
    queryset = AuditItem.objects.all()
    serializer_class = AuditItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset.order_by('-timestamp')

class HealthMetricViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing health metrics.
    
    list:
    Return a list of all health metrics.
    
    create:
    Create a new health metric.
    
    retrieve:
    Return the details of a specific health metric.
    
    update:
    Update all fields of a specific health metric.
    
    partial_update:
    Update one or more fields of a specific health metric.
    
    destroy:
    Delete a specific health metric.
    """
    queryset = HealthMetric.objects.all()
    serializer_class = HealthMetricSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransferVolumeDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transfer volume data.
    
    list:
    Return a list of all transfer volume data.
    
    create:
    Create a new transfer volume data.
    
    retrieve:
    Return the details of a specific transfer volume data.
    
    update:
    Update all fields of a specific transfer volume data.
    
    partial_update:
    Update one or more fields of a specific transfer volume data.
    
    destroy:
    Delete a specific transfer volume data.
    """
    queryset = TransferVolumeData.objects.all()
    serializer_class = TransferVolumeDataSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProcessingTimeDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing processing time data.
    
    list:
    Return a list of all processing time data.
    
    create:
    Create a new processing time data.
    
    retrieve:
    Return the details of a specific processing time data.
    
    update:
    Update all fields of a specific processing time data.
    
    partial_update:
    Update one or more fields of a specific processing time data.
    
    destroy:
    Delete a specific processing time data.
    """
    queryset = ProcessingTimeData.objects.all()
    serializer_class = ProcessingTimeDataSerializer
    permission_classes = [permissions.IsAuthenticated]

class AgentSuccessDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing agent success data.
    
    list:
    Return a list of all agent success data.
    
    create:
    Create a new agent success data.
    
    retrieve:
    Return the details of a specific agent success data.
    
    update:
    Update all fields of a specific agent success data.
    
    partial_update:
    Update one or more fields of a specific agent success data.
    
    destroy:
    Delete a specific agent success data.
    """
    queryset = AgentSuccessData.objects.all()
    serializer_class = AgentSuccessDataSerializer
    permission_classes = [permissions.IsAuthenticated]

class DashboardMetricsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dashboard metrics.
    
    list:
    Return a list of all dashboard metrics.
    
    create:
    Create a new dashboard metric.
    
    retrieve:
    Return the details of a specific dashboard metric.
    
    update:
    Update all fields of a specific dashboard metric.
    
    partial_update:
    Update one or more fields of a specific dashboard metric.
    
    destroy:
    Delete a specific dashboard metric.
    """
    queryset = DashboardMetrics.objects.all()
    serializer_class = DashboardMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="Get the latest metrics",
        responses={
            200: DashboardMetricsSerializer,
            404: "No metrics found"
        }
    )
    @action(detail=False, methods=['get'])
    def latest(self, request):
        metrics = self.get_queryset().order_by('-timestamp').first()
        if not metrics:
            return Response(
                {'error': 'No metrics available'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(metrics)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get a summary of key metrics",
        responses={
            200: "Summary of key metrics",
            404: "No metrics found"
        }
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        metrics = self.get_queryset().order_by('-timestamp').first()
        if not metrics:
            return Response(
                {'error': 'No metrics available'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({
            'total_transfers': metrics.total_transfers,
            'active_agents': metrics.active_agents,
            'success_rate': metrics.success_rate,
            'average_processing_time': metrics.average_processing_time
        })

    @swagger_auto_schema(
        operation_description="Get the latest notifications",
        responses={
            200: NotificationItemSerializer(many=True),
            404: "No notifications found"
        }
    )
    @action(detail=False, methods=['get'])
    def notifications(self, request):
        notifications = NotificationItem.objects.all().order_by('-timestamp')[:10]
        serializer = NotificationItemSerializer(notifications, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get the latest activities",
        responses={
            200: ActivityItemSerializer(many=True),
            404: "No activities found"
        }
    )
    @action(detail=False, methods=['get'])
    def activities(self, request):
        activities = ActivityItem.objects.all().order_by('-timestamp')[:10]
        serializer = ActivityItemSerializer(activities, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get overdue units",
        responses={
            200: OverdueUnitSerializer(many=True),
            404: "No overdue units found"
        }
    )
    @action(detail=False, methods=['get'])
    def overdue_units(self, request):
        overdue_units = OverdueUnit.objects.all().order_by('-overdue_count')
        serializer = OverdueUnitSerializer(overdue_units, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get the latest audit items",
        responses={
            200: AuditItemSerializer(many=True),
            404: "No audit items found"
        }
    )
    @action(detail=False, methods=['get'])
    def audit_trail(self, request):
        audit_items = AuditItem.objects.all().order_by('-timestamp')[:20]
        serializer = AuditItemSerializer(audit_items, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get health metrics",
        responses={
            200: HealthMetricSerializer(many=True),
            404: "No health metrics found"
        }
    )
    @action(detail=False, methods=['get'])
    def health_metrics(self, request):
        health_metrics = HealthMetric.objects.all()
        serializer = HealthMetricSerializer(health_metrics, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get transfer volume data",
        responses={
            200: TransferVolumeDataSerializer(many=True),
            404: "No transfer volume data found"
        }
    )
    @action(detail=False, methods=['get'])
    def transfer_volume(self, request):
        volume_data = TransferVolumeData.objects.all().order_by('-timestamp').first()
        if not volume_data:
            return Response(
                {'error': 'No transfer volume data available'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TransferVolumeDataSerializer(volume_data)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get processing time data",
        responses={
            200: ProcessingTimeDataSerializer(many=True),
            404: "No processing time data found"
        }
    )
    @action(detail=False, methods=['get'])
    def processing_time(self, request):
        time_data = ProcessingTimeData.objects.all().order_by('-timestamp').first()
        if not time_data:
            return Response(
                {'error': 'No processing time data available'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProcessingTimeDataSerializer(time_data)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get agent success data",
        responses={
            200: AgentSuccessDataSerializer(many=True),
            404: "No agent success data found"
        }
    )
    @action(detail=False, methods=['get'])
    def agent_success(self, request):
        success_data = AgentSuccessData.objects.all().order_by('-timestamp').first()
        if not success_data:
            return Response(
                {'error': 'No agent success data available'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AgentSuccessDataSerializer(success_data)
        return Response(serializer.data)
