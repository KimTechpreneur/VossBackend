from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import timedelta
import csv
from io import StringIO
from .models import Agent, AgentDelivery, BaseOffice
from .serializers import (
    AgentSerializer, AgentListSerializer, AgentDeliverySerializer,
    AgentDeliveryListSerializer, AgentBulkUpdateSerializer, BaseOfficeSerializer
)
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminUser, IsOwnerOrAdmin, IsAgentManager

# Create your views here.

class BaseOfficeViewSet(viewsets.ModelViewSet):
    queryset = BaseOffice.objects.all()
    serializer_class = BaseOfficeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class AgentDeliveryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing agent deliveries.
    
    list:
    Return a list of all agent deliveries.
    
    create:
    Create a new agent delivery.
    
    retrieve:
    Return the details of a specific agent delivery.
    
    update:
    Update all fields of a specific agent delivery.
    
    partial_update:
    Update one or more fields of a specific agent delivery.
    
    destroy:
    Delete a specific agent delivery.
    """
    serializer_class = AgentDeliverySerializer
    permission_classes = [IsAuthenticated, IsAgentManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'confirmation_type']
    search_fields = ['delivery_id', 'from_location', 'to_location']
    ordering_fields = ['date', 'status', 'time_taken']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.action == 'list':
            return AgentDeliveryListSerializer
        return AgentDeliverySerializer

    def get_queryset(self):
        agent_id = self.kwargs.get('agent_pk')
        queryset = AgentDelivery.objects.filter(agent_id=agent_id)
        
        # Filter by date range
        date_range = self.request.query_params.get('dateRange')
        from_date = self.request.query_params.get('from')
        to_date = self.request.query_params.get('to')
        
        if date_range:
            today = timezone.now().date()
            if date_range == 'week':
                from_date = today - timedelta(days=7)
                to_date = today
            elif date_range == 'month':
                from_date = today - timedelta(days=30)
                to_date = today
            elif date_range == 'year':
                from_date = today - timedelta(days=365)
                to_date = today
        
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
            
        return queryset

    @swagger_auto_schema(
        operation_description="Mark a delivery as delivered",
        responses={
            200: "Delivery marked as delivered successfully",
            404: "Delivery not found"
        }
    )
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        delivery = self.get_object()
        delivery.status = 'delivered'
        delivery.save()
        return Response({'status': 'delivery marked as delivered'})

class AgentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing agents.
    
    list:
    Return a list of all agents.
    
    create:
    Create a new agent.
    
    retrieve:
    Return the details of a specific agent.
    
    update:
    Update all fields of a specific agent.
    
    partial_update:
    Update one or more fields of a specific agent.
    
    destroy:
    Delete a specific agent.
    """
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated, IsAgentManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'base_office', 'employment_type']
    search_fields = ['user__full_name', 'user__email', 'agent_id', 'base_office__name']
    ordering_fields = [
        'user__full_name', 'user__email', 'status', 'base_office__name',
        'joined_date', 'last_activity', 'deliveries_today', 'success_rate'
    ]
    ordering = ['-last_activity']

    def get_serializer_class(self):
        if self.action == 'list':
            return AgentListSerializer
        return AgentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by joined date range
        joined_date_from = self.request.query_params.get('joinedDateFrom')
        joined_date_to = self.request.query_params.get('joinedDateTo')
        
        if joined_date_from:
            queryset = queryset.filter(joined_date__gte=joined_date_from)
        if joined_date_to:
            queryset = queryset.filter(joined_date__lte=joined_date_to)
            
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        serializer = AgentBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            agent_ids = serializer.validated_data['agent_ids']
            agents = Agent.objects.filter(id__in=agent_ids)
            agents.update(status='suspended')
            return Response({'message': 'Selected agents deactivated successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        format_type = request.query_params.get('format', 'csv')
        
        if format_type == 'csv':
            output = StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow([
                'ID', 'Name', 'Email', 'Phone', 'Status', 'Base Office',
                'Employment Type', 'Joined Date', 'Last Activity',
                'Deliveries Today', 'Success Rate'
            ])
            
            # Write data
            for agent in queryset:
                writer.writerow([
                    agent.id,
                    agent.user.full_name,
                    agent.user.email,
                    agent.user.phone,
                    agent.status,
                    agent.base_office.name,
                    agent.employment_type,
                    agent.joined_date,
                    agent.last_activity,
                    agent.deliveries_today,
                    agent.success_rate
                ])
            
            output.seek(0)
            response = Response(output.getvalue())
            response['Content-Type'] = 'text/csv'
            response['Content-Disposition'] = 'attachment; filename=agents.csv'
            return response
            
        return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Assign a delivery to an agent",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['delivery_id'],
            properties={
                'delivery_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the delivery to assign')
            }
        ),
        responses={
            200: "Delivery assigned successfully",
            400: "Bad Request",
            404: "Agent or delivery not found"
        }
    )
    @action(detail=True, methods=['post'])
    def assign_delivery(self, request, pk=None):
        agent = self.get_object()
        delivery_id = request.data.get('delivery_id')
        
        if not delivery_id:
            return Response(
                {'error': 'delivery_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            delivery = AgentDelivery.objects.get(id=delivery_id)
            delivery.agent = agent
            delivery.save()
            return Response({'status': 'delivery assigned'})
        except AgentDelivery.DoesNotExist:
            return Response(
                {'error': 'Delivery not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        agent = self.get_object()
        deliveries = AgentDelivery.objects.filter(agent=agent)
        serializer = AgentDeliverySerializer(deliveries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def deliveries_today(self, request, pk=None):
        agent = self.get_object()
        today = timezone.now().date()
        deliveries = AgentDelivery.objects.filter(
            agent=agent,
            date=today
        )
        serializer = AgentDeliverySerializer(deliveries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance_metrics(self, request, pk=None):
        agent = self.get_object()
        total_deliveries = AgentDelivery.objects.filter(agent=agent).count()
        completed_deliveries = AgentDelivery.objects.filter(
            agent=agent,
            status='completed'
        ).count()
        
        success_rate = (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        return Response({
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed_deliveries,
            'success_rate': success_rate
        })
