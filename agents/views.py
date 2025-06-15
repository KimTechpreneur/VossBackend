from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from datetime import timedelta
import csv
from io import StringIO
from .models import Agent, AgentDelivery
from offices.models import Office
from .serializers import (
    AgentSerializer, AgentListSerializer, AgentDeliverySerializer,
    AgentDeliveryListSerializer, AgentBulkUpdateSerializer,
    AgentCreateSerializer, HybridAgentListSerializer, AgentUpgradeSerializer
)
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminUser, IsOwnerOrAdmin, IsAgentManager
from users.models import User, Role

# Create your views here.

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
    Return a list of all agents (including users with agent role but no profile).
    
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
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'agent_id', 'base_office__office_name']
    ordering_fields = [
        'user__first_name', 'user__last_name', 'user__email', 'status', 'base_office__office_name',
        'joined_date', 'last_activity', 'deliveries_today', 'success_rate'
    ]
    ordering = ['-last_activity']

    def get_serializer_class(self):
        if self.action == 'list':
            return HybridAgentListSerializer
        if self.action == 'create':
            return AgentCreateSerializer
        if self.action == 'upgrade_user':
            return AgentUpgradeSerializer
        return AgentSerializer

    def list(self, request, *args, **kwargs):
        """
        Custom list method to show both full agents and users with agent role
        """
        # Get all users with Agent role
        try:
            agent_role = Role.objects.get(name='Agent')
            agent_users = User.objects.filter(role=agent_role)
        except Role.DoesNotExist:
            agent_users = User.objects.none()

        hybrid_agents = []
        
        for user in agent_users:
            # Check if user has an agent profile
            has_agent_profile = hasattr(user, 'agent')
            
            # Get full name from first_name and last_name
            full_name = f"{user.first_name} {user.last_name}".strip()
            if not full_name:
                full_name = user.email.split('@')[0]  # Fallback to email username
            
            if has_agent_profile:
                agent = user.agent
                hybrid_agent = {
                    'id': str(agent.id),
                    'name': full_name,
                    'email': user.email,
                    'phone': user.phone or '',
                    'status': agent.status,
                    'base_office': agent.base_office.office_name if agent.base_office else '',
                    'employment_type': agent.employment_type,
                    'joined_date': agent.joined_date,
                    'last_activity': agent.last_activity,
                    'deliveries_today': agent.deliveries_today,
                    'success_rate': agent.success_rate,
                    'initials': user.initials,
                    'has_agent_profile': True,
                    'user_id': str(user.id)
                }
            else:
                # User with agent role but no profile
                hybrid_agent = {
                    'id': str(user.id),  # Use user ID for potential agents
                    'name': full_name,
                    'email': user.email,
                    'phone': user.phone or '',
                    'status': 'pending_setup',  # Special status for incomplete profiles
                    'base_office': '',
                    'employment_type': '',
                    'joined_date': user.date_joined,
                    'last_activity': user.last_login,
                    'deliveries_today': 0,
                    'success_rate': 0,
                    'initials': user.initials,
                    'has_agent_profile': False,
                    'user_id': str(user.id)
                }
            
            hybrid_agents.append(hybrid_agent)

        # Apply search filtering
        search = request.query_params.get('search', '')
        if search:
            hybrid_agents = [
                agent for agent in hybrid_agents
                if search.lower() in agent['name'].lower() or 
                   search.lower() in agent['email'].lower()
            ]

        # Filter for agents with profiles if requested
        has_profile = request.query_params.get('has_profile', 'false').lower()
        if has_profile == 'true':
            hybrid_agents = [
                agent for agent in hybrid_agents if agent.get('has_agent_profile')
            ]

        # Apply status filtering
        status_filter = request.query_params.get('status', '')
        if status_filter and status_filter != 'all':
            hybrid_agents = [
                agent for agent in hybrid_agents
                if agent['status'] == status_filter
            ]

        # Pagination
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_agents = hybrid_agents[start:end]
        
        serializer = HybridAgentListSerializer(paginated_agents, many=True)
        
        return Response({
            'results': serializer.data,
            'count': len(hybrid_agents)
        })

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method to handle both agent IDs and user IDs
        """
        pk = kwargs.get('pk')
        
        # First try to get as an Agent
        try:
            agent = Agent.objects.get(id=pk)
            serializer = AgentSerializer(agent)
            return Response(serializer.data)
        except (Agent.DoesNotExist, ValueError):
            pass
        
        # If not found as Agent, try to get as User with Agent role
        try:
            agent_role = Role.objects.get(name='Agent')
            user = User.objects.get(id=pk, role=agent_role)
            
            # Check if user has an agent profile
            if hasattr(user, 'agent'):
                # User has agent profile, return full agent data
                serializer = AgentSerializer(user.agent)
                return Response(serializer.data)
            else:
                # User has no agent profile, return basic user data as potential agent
                full_name = f"{user.first_name} {user.last_name}".strip()
                if not full_name:
                    full_name = user.email.split('@')[0]
                
                potential_agent_data = {
                    'id': str(user.id),
                    'user': {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'phone': user.phone or '',
                        'initials': user.initials
                    },
                    'status': 'pending_setup',
                    'base_office': None,
                    'employment_type': '',
                    'joined_date': user.date_joined,
                    'last_activity': user.last_login,
                    'deliveries_today': 0,
                    'success_rate': 0,
                    'has_agent_profile': False
                }
                return Response(potential_agent_data)
                
        except (User.DoesNotExist, Role.DoesNotExist, ValueError):
            pass
        
        # If neither found, return 404
        return Response(
            {'detail': 'Agent not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    def update(self, request, *args, **kwargs):
        """
        Custom update method to handle both agent updates and user updates
        """
        pk = kwargs.get('pk')
        
        # First try to get as an Agent
        try:
            agent = Agent.objects.get(id=pk)
            # Update agent fields
            serializer = AgentSerializer(agent, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (Agent.DoesNotExist, ValueError):
            pass
        
        # If not found as Agent, try to get as User with Agent role
        try:
            agent_role = Role.objects.get(name='Agent')
            user = User.objects.get(id=pk, role=agent_role)
            
            # Check if user has an agent profile
            if hasattr(user, 'agent'):
                # User has agent profile, update the agent
                agent = user.agent
                serializer = AgentSerializer(agent, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                # User has no agent profile, can only update basic user info
                user_data = request.data.get('user', {})
                if user_data:
                    for field, value in user_data.items():
                        if hasattr(user, field):
                            setattr(user, field, value)
                    user.save()
                
                # Return updated user data as potential agent
                full_name = f"{user.first_name} {user.last_name}".strip()
                if not full_name:
                    full_name = user.email.split('@')[0]
                
                potential_agent_data = {
                    'id': str(user.id),
                    'user': {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'phone': user.phone or '',
                        'initials': user.initials
                    },
                    'status': 'pending_setup',
                    'base_office': None,
                    'employment_type': '',
                    'joined_date': user.date_joined,
                    'last_activity': user.last_login,
                    'deliveries_today': 0,
                    'success_rate': 0,
                    'has_agent_profile': False
                }
                return Response(potential_agent_data)
                
        except (User.DoesNotExist, Role.DoesNotExist, ValueError):
            pass
        
        # If neither found, return 404
        return Response(
            {'detail': 'Agent not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=['post'])
    def upgrade_user(self, request):
        """
        Upgrade a user with agent role to a full agent with profile
        """
        serializer = AgentUpgradeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                agent = serializer.save()
                return Response({
                    'message': 'User successfully upgraded to agent',
                    'agent_id': str(agent.id)
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get agent statistics summary including both full agents and potential agents.
        """
        # Get all users with Agent role
        try:
            agent_role = Role.objects.get(name='Agent')
            total_agent_users = User.objects.filter(role=agent_role).count()
        except Role.DoesNotExist:
            total_agent_users = 0

        # Get full agents
        full_agents = Agent.objects.all()
        active_today = full_agents.filter(status='available').count()
        in_transit = full_agents.filter(status='in_transit').count()
        
        # Calculate flagged deliveries (with exception status)
        flagged_deliveries = AgentDelivery.objects.filter(status='exception').count()
        
        # Calculate new agents this month
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = full_agents.filter(joined_date__gte=first_day_of_month).count()
        
        stats = {
            'totalAgents': total_agent_users,  # Include both full and potential agents
            'activeToday': active_today,
            'inTransit': in_transit,
            'flaggedDeliveries': flagged_deliveries,
            'newThisMonth': new_this_month
        }
        
        return Response(stats)

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
                    f"{agent.user.first_name} {agent.user.last_name}",
                    agent.user.email,
                    agent.user.phone,
                    agent.status,
                    agent.base_office.office_name,
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
            date__date=today
        )
        serializer = AgentDeliverySerializer(deliveries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance_metrics(self, request, pk=None):
        agent = self.get_object()
        
        # Calculate performance metrics
        total_deliveries = agent.deliveries.count()
        completed_deliveries = agent.deliveries.filter(status='completed').count()
        success_rate = (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # Get deliveries for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_deliveries = agent.deliveries.filter(date__gte=thirty_days_ago)
        
        metrics = {
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed_deliveries,
            'success_rate': round(success_rate, 2),
            'recent_deliveries_count': recent_deliveries.count(),
            'average_deliveries_per_day': round(recent_deliveries.count() / 30, 2)
        }
        
        return Response(metrics)
