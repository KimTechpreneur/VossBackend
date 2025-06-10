from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    SearchResultItem, SearchFilters, TransferPathStep,
    AgentActivity, TransferTrail, SearchHistory, SearchResult
)
from .serializers import (
    SearchResultItemSerializer, SearchFiltersSerializer,
    TransferPathStepSerializer, AgentActivitySerializer,
    TransferTrailSerializer, SearchBulkUpdateSerializer,
    SearchHistorySerializer, SearchResultSerializer
)
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminUser, IsOwnerOrAdmin

# Create your views here.

class TransferPathStepViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transfer path steps.
    
    list:
    Return a list of all transfer path steps.
    
    create:
    Create a new transfer path step.
    
    retrieve:
    Return the details of a specific transfer path step.
    
    update:
    Update all fields of a specific transfer path step.
    
    partial_update:
    Update one or more fields of a specific transfer path step.
    
    destroy:
    Delete a specific transfer path step.
    """
    queryset = TransferPathStep.objects.all()
    serializer_class = TransferPathStepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        folder_id = self.request.query_params.get('folder', None)
        office_id = self.request.query_params.get('office', None)
        status = self.request.query_params.get('status', None)
        
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        if office_id:
            queryset = queryset.filter(office_id=office_id)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('timestamp')

class AgentActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing agent activities.
    
    list:
    Return a list of all agent activities.
    
    create:
    Create a new agent activity.
    
    retrieve:
    Return the details of a specific agent activity.
    
    update:
    Update all fields of a specific agent activity.
    
    partial_update:
    Update one or more fields of a specific agent activity.
    
    destroy:
    Delete a specific agent activity.
    """
    queryset = AgentActivity.objects.all()
    serializer_class = AgentActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        transfer_id = self.request.query_params.get('transfer', None)
        agent_id = self.request.query_params.get('agent', None)
        status = self.request.query_params.get('status', None)
        
        if transfer_id:
            queryset = queryset.filter(transfer_id=transfer_id)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-timestamp')

class TransferTrailViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transfer trails.
    
    list:
    Return a list of all transfer trails.
    
    create:
    Create a new transfer trail.
    
    retrieve:
    Return the details of a specific transfer trail.
    
    update:
    Update all fields of a specific transfer trail.
    
    partial_update:
    Update one or more fields of a specific transfer trail.
    
    destroy:
    Delete a specific transfer trail.
    """
    queryset = TransferTrail.objects.all()
    serializer_class = TransferTrailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        folder_id = self.request.query_params.get('folder', None)
        
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
            
        return queryset

class SearchFiltersViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing search filters.
    
    list:
    Return a list of all search filters.
    
    create:
    Create a new search filter.
    
    retrieve:
    Return the details of a specific search filter.
    
    update:
    Update all fields of a specific search filter.
    
    partial_update:
    Update one or more fields of a specific search filter.
    
    destroy:
    Delete a specific search filter.
    """
    queryset = SearchFilters.objects.all()
    serializer_class = SearchFiltersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.order_by('-created_at')

class SearchResultItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing search result items.
    
    list:
    Return a list of all search result items.
    
    create:
    Create a new search result item.
    
    retrieve:
    Return the details of a specific search result item.
    
    update:
    Update all fields of a specific search result item.
    
    partial_update:
    Update one or more fields of a specific search result item.
    
    destroy:
    Delete a specific search result item.
    """
    queryset = SearchResultItem.objects.all()
    serializer_class = SearchResultItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        current_status = self.request.query_params.get('current_status', None)
        current_office = self.request.query_params.get('current_office', None)
        
        if current_status:
            queryset = queryset.filter(current_status=current_status)
        if current_office:
            queryset = queryset.filter(current_office_id=current_office)
            
        return queryset.order_by('-last_activity')

    @swagger_auto_schema(
        operation_description="Bulk update multiple search result items",
        request_body=SearchBulkUpdateSerializer,
        responses={
            200: "Search results updated successfully",
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        serializer = SearchBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            search_result_ids = serializer.validated_data['search_result_ids']
            results = SearchResultItem.objects.filter(id__in=search_result_ids)
            
            if 'current_status' in serializer.validated_data:
                results.update(current_status=serializer.validated_data['current_status'])
            if 'current_office' in serializer.validated_data:
                results.update(current_office=serializer.validated_data['current_office'])
                
            return Response({'status': 'search results updated'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Search for items based on various filters",
        responses={
            200: SearchResultItemSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        search_term = request.query_params.get('q', '')
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        destination_unit = request.query_params.get('destination_unit', None)
        office = request.query_params.get('office', None)
        file_type = request.query_params.get('file_type', None)
        current_status = request.query_params.get('current_status', None)
        agent = request.query_params.get('agent', None)
        treatment_folder_id = request.query_params.get('treatment_folder_id', None)
        specific_file_id = request.query_params.get('specific_file_id', None)

        # Create search filters
        filters = SearchFilters.objects.create(
            search_term=search_term,
            date_from=date_from,
            date_to=date_to,
            destination_unit=destination_unit,
            office=office,
            file_type=file_type,
            current_status=current_status,
            agent=agent,
            treatment_folder_id=treatment_folder_id,
            specific_file_id=specific_file_id
        )

        # Perform search based on filters
        results = SearchResultItem.objects.all()
        
        if search_term:
            results = results.filter(
                folder__title__icontains=search_term
            ) | results.filter(
                folder__subject__icontains=search_term
            )
        if date_from:
            results = results.filter(last_activity__gte=date_from)
        if date_to:
            results = results.filter(last_activity__lte=date_to)
        if destination_unit:
            results = results.filter(folder__destination_office=destination_unit)
        if office:
            results = results.filter(current_office=office)
        if file_type:
            results = results.filter(file__file_type=file_type)
        if current_status:
            results = results.filter(current_status=current_status)
        if agent:
            results = results.filter(folder__assigned_agent=agent)
        if treatment_folder_id:
            results = results.filter(folder__folder_id=treatment_folder_id)
        if specific_file_id:
            results = results.filter(file__id=specific_file_id)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

class SearchHistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing search history.
    
    list:
    Return a list of all search history items.
    
    create:
    Create a new search history item.
    
    retrieve:
    Return the details of a specific search history item.
    
    update:
    Update all fields of a specific search history item.
    
    partial_update:
    Update one or more fields of a specific search history item.
    
    destroy:
    Delete a specific search history item.
    """
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SearchHistory.objects.none()
        user = self.request.user
        queryset = SearchHistory.objects.all()
        queryset = queryset.filter(user=user)
        return queryset

    @swagger_auto_schema(
        operation_description="Clear search history",
        responses={
            200: "Search history cleared successfully",
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['post'])
    def clear_history(self, request):
        user = request.user
        self.get_queryset().filter(user=user).delete()
        return Response({'status': 'search history cleared'})

class SearchResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing search results.
    
    list:
    Return a list of all search results.
    
    create:
    Create a new search result.
    
    retrieve:
    Return the details of a specific search result.
    
    update:
    Update all fields of a specific search result.
    
    partial_update:
    Update one or more fields of a specific search result.
    
    destroy:
    Delete a specific search result.
    """
    queryset = SearchResult.objects.all()
    serializer_class = SearchResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_id = self.request.query_params.get('search_id', None)
        result_type = self.request.query_params.get('type', None)
        
        if search_id:
            queryset = queryset.filter(search_id=search_id)
        if result_type:
            queryset = queryset.filter(result_type=result_type)
            
        return queryset.select_related('search')

    @swagger_auto_schema(
        operation_description="Get search results by type",
        responses={
            200: SearchResultSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        result_type = request.query_params.get('type')
        if not result_type:
            return Response(
                {'error': 'type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        results = self.get_queryset().filter(result_type=result_type)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get search results by search ID",
        responses={
            200: SearchResultSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def by_search(self, request):
        search_id = request.query_params.get('search_id')
        if not search_id:
            return Response(
                {'error': 'search_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        results = self.get_queryset().filter(search_id=search_id)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
