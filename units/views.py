from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from .models import Unit
from .serializers import (
    UnitSerializer, UnitListSerializer,
    UnitStatusOptionSerializer, UnitTypeOptionSerializer,
    HeadOfUnitOptionSerializer
)
from users.permissions import IsAdminUser

class UnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing units.
    
    list:
    Return a list of all units.
    
    create:
    Create a new unit.
    
    retrieve:
    Return the details of a specific unit.
    
    update:
    Update all fields of a specific unit.
    
    partial_update:
    Update one or more fields of a specific unit.
    
    destroy:
    Delete a specific unit.
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'bulk_update']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters
        search_query = self.request.query_params.get('searchQuery', '')
        unit_type = self.request.query_params.get('unitType', 'all')
        status = self.request.query_params.get('status', 'all')
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(unit_code__icontains=search_query)
            )
        
        # Apply type filter
        if unit_type != 'all':
            queryset = queryset.filter(unit_type=unit_type)
            
        # Apply status filter
        if status != 'all':
            queryset = queryset.filter(status=status)
            
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return UnitListSerializer
        return UnitSerializer

    @swagger_auto_schema(
        operation_description="Toggle unit status between active and inactive",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['active', 'inactive']
                )
            },
            required=['status']
        ),
        responses={
            200: UnitSerializer,
            400: "Bad Request",
            404: "Unit not found"
        }
    )
    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        unit = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['active', 'inactive']:
            return Response(
                {'error': 'Invalid status value'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        unit.status = new_status
        unit.save()
        serializer = self.get_serializer(unit)
        return Response(serializer.data)

class UnitOptionsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get list of available unit types",
        responses={
            200: UnitTypeOptionSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def unit_types(self, request):
        unit_types = [
            {'value': 'central_admin', 'label': 'Central Administration'},
            {'value': 'academic_faculty', 'label': 'Academic Faculty'},
            {'value': 'support_service', 'label': 'Support Service'},
            {'value': 'health_services', 'label': 'Health Services'},
            {'value': 'finance_division', 'label': 'Finance Division'},
            {'value': 'audit_unit', 'label': 'Audit Unit'},
            {'value': 'other', 'label': 'Other'}
        ]
        serializer = UnitTypeOptionSerializer(unit_types, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get list of available unit statuses",
        responses={
            200: UnitStatusOptionSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def unit_statuses(self, request):
        statuses = [
            {'value': 'active', 'label': 'Active'},
            {'value': 'inactive', 'label': 'Inactive'},
            {'value': 'archived', 'label': 'Archived'}
        ]
        serializer = UnitStatusOptionSerializer(statuses, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get list of available head of unit options",
        responses={
            200: HeadOfUnitOptionSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def head_of_unit(self, request):
        users = User.objects.filter(is_active=True)
        serializer = HeadOfUnitOptionSerializer(users, many=True)
        return Response(serializer.data)
