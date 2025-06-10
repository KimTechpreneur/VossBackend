from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    InternalOffice, OfficeStaffMember,
    OfficeFolder, OfficeTransfer
)
from .serializers import (
    InternalOfficeSerializer, OfficeStaffMemberSerializer,
    OfficeFolderSerializer, OfficeTransferSerializer,
    OfficeBulkUpdateSerializer
)
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminUser, IsOwnerOrAdmin

# Create your views here.

class OfficeStaffMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing office staff members.
    
    list:
    Return a list of all office staff members.
    
    create:
    Create a new office staff member.
    
    retrieve:
    Return the details of a specific office staff member.
    
    update:
    Update all fields of a specific office staff member.
    
    partial_update:
    Update one or more fields of a specific office staff member.
    
    destroy:
    Delete a specific office staff member.
    """
    queryset = OfficeStaffMember.objects.all()
    serializer_class = OfficeStaffMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        office_id = self.request.query_params.get('office_id', None)
        role = self.request.query_params.get('role', None)
        status = self.request.query_params.get('status', None)
        
        if office_id:
            queryset = queryset.filter(office_id=office_id)
        if role:
            queryset = queryset.filter(role=role)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.select_related('office', 'user')

    @swagger_auto_schema(
        operation_description="Deactivate a staff member",
        responses={
            200: "Staff member deactivated successfully",
            404: "Staff member not found"
        }
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        staff_member = self.get_object()
        staff_member.status = 'inactive'
        staff_member.save()
        return Response({'status': 'staff member deactivated'})

class OfficeFolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing office folders.
    
    list:
    Return a list of all office folders.
    
    create:
    Create a new office folder.
    
    retrieve:
    Return the details of a specific office folder.
    
    update:
    Update all fields of a specific office folder.
    
    partial_update:
    Update one or more fields of a specific office folder.
    
    destroy:
    Delete a specific office folder.
    """
    queryset = OfficeFolder.objects.all()
    serializer_class = OfficeFolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        office_id = self.request.query_params.get('office_id', None)
        status = self.request.query_params.get('status', None)
        
        if office_id:
            queryset = queryset.filter(office_id=office_id)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.select_related('office', 'folder', 'initiated_by')

    @swagger_auto_schema(
        operation_description="Complete an office folder",
        responses={
            200: "Folder completed successfully",
            404: "Folder not found"
        }
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        office_folder = self.get_object()
        office_folder.status = 'completed'
        office_folder.save()
        return Response({'status': 'office folder completed'})

class OfficeTransferViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing office transfers.
    
    list:
    Return a list of all office transfers.
    
    create:
    Create a new office transfer.
    
    retrieve:
    Return the details of a specific office transfer.
    
    update:
    Update all fields of a specific office transfer.
    
    partial_update:
    Update one or more fields of a specific office transfer.
    
    destroy:
    Delete a specific office transfer.
    """
    queryset = OfficeTransfer.objects.all()
    serializer_class = OfficeTransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        office_id = self.request.query_params.get('office_id', None)
        status = self.request.query_params.get('status', None)
        party = self.request.query_params.get('party', None)
        
        if office_id:
            queryset = queryset.filter(office_id=office_id)
        if status:
            queryset = queryset.filter(status=status)
        if party:
            queryset = queryset.filter(party=party)
            
        return queryset.select_related('office', 'transfer')

    @swagger_auto_schema(
        operation_description="Complete an office transfer",
        responses={
            200: "Transfer completed successfully",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        office_transfer = self.get_object()
        office_transfer.status = 'completed'
        office_transfer.save()
        return Response({'status': 'office transfer completed'})

class InternalOfficeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing internal offices.
    
    list:
    Return a list of all internal offices.
    
    create:
    Create a new internal office.
    
    retrieve:
    Return the details of a specific internal office.
    
    update:
    Update all fields of a specific internal office.
    
    partial_update:
    Update one or more fields of a specific internal office.
    
    destroy:
    Delete a specific internal office.
    """
    queryset = InternalOffice.objects.all()
    serializer_class = InternalOfficeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'bulk_update']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        office_type = self.request.query_params.get('office_type', None)
        status = self.request.query_params.get('status', None)
        parent_office = self.request.query_params.get('parent_office', None)
        
        if office_type:
            queryset = queryset.filter(office_type=office_type)
        if status:
            queryset = queryset.filter(status=status)
        if parent_office:
            queryset = queryset.filter(parent_office_id=parent_office)
            
        return queryset.select_related('head_of_office', 'parent_office')

    @swagger_auto_schema(
        operation_description="Bulk update multiple internal offices",
        request_body=InternalOfficeSerializer(many=True),
        responses={
            200: InternalOfficeSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admin users can perform bulk updates."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data)
    
    def perform_bulk_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        office = self.get_object()
        office.status = 'inactive'
        office.save()
        return Response({'status': 'office deactivated'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        office = self.get_object()
        office.status = 'active'
        office.save()
        return Response({'status': 'office activated'})

    @action(detail=True, methods=['get'])
    def staff_members(self, request, pk=None):
        office = self.get_object()
        staff_members = OfficeStaffMember.objects.filter(office=office)
        serializer = OfficeStaffMemberSerializer(staff_members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def folders(self, request, pk=None):
        office = self.get_object()
        folders = OfficeFolder.objects.filter(office=office)
        serializer = OfficeFolderSerializer(folders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transfers(self, request, pk=None):
        office = self.get_object()
        transfers = OfficeTransfer.objects.filter(office=office)
        serializer = OfficeTransferSerializer(transfers, many=True)
        return Response(serializer.data)
