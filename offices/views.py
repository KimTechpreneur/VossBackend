from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Office, OfficeFolder, OfficeTransfer
)
from .serializers import (
    OfficeSerializer, OfficeDetailSerializer,
    OfficeFolderSerializer, OfficeTransferSerializer
)
from users.permissions import IsAdminUser, IsOwnerOrAdmin

# Create your views here.

class OfficeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing offices.
    
    list:
    Return a list of all offices.
    
    create:
    Create a new office.
    
    retrieve:
    Return the details of a specific office.
    
    update:
    Update all fields of a specific office.
    
    partial_update:
    Update one or more fields of a specific office.
    
    destroy:
    Delete a specific office.
    """
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OfficeDetailSerializer
        return OfficeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        office_type = self.request.query_params.get('office_type', None)
        status = self.request.query_params.get('status', None)
        
        if office_type:
            queryset = queryset.filter(office_type=office_type)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.select_related('head_of_office', 'updated_by')

    @swagger_auto_schema(
        operation_description="Get office statistics",
        responses={
            200: openapi.Response(
                description="Office statistics",
                examples={
                    "application/json": {
                        "total_offices": 10,
                        "active_offices": 8,
                        "inactive_offices": 2,
                        "total_transfers": 25,
                        "total_folders": 100
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get office statistics"""
        total_offices = Office.objects.count()
        active_offices = Office.objects.filter(status='Active').count()
        inactive_offices = Office.objects.filter(status='Inactive').count()
        total_transfers = OfficeTransfer.objects.count()
        total_folders = OfficeFolder.objects.count()
        
        return Response({
            'total_offices': total_offices,
            'active_offices': active_offices,
            'inactive_offices': inactive_offices,
            'total_transfers': total_transfers,
            'total_folders': total_folders
        })

    @swagger_auto_schema(
        operation_description="Activate an office",
        responses={
            200: "Office activated successfully",
            404: "Office not found"
        }
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an office"""
        office = self.get_object()
        office.status = 'Active'
        office.updated_by = request.user
        office.save()
        return Response({'status': 'office activated'})

    @swagger_auto_schema(
        operation_description="Deactivate an office",
        responses={
            200: "Office deactivated successfully",
            404: "Office not found"
        }
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an office"""
        office = self.get_object()
        office.status = 'Inactive'
        office.updated_by = request.user
        office.save()
        return Response({'status': 'office deactivated'})

    @swagger_auto_schema(
        operation_description="Bulk update multiple offices",
        request_body=OfficeSerializer(many=True),
        responses={
            200: OfficeSerializer(many=True),
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update multiple offices"""
        serializer = OfficeSerializer(data=request.data, many=True)
        if serializer.is_valid():
            offices = serializer.save()
            return Response(OfficeSerializer(offices, many=True).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Bulk delete multiple offices",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'office_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            }
        ),
        responses={
            200: "Offices deleted successfully",
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete multiple offices"""
        office_ids = request.data.get('office_ids', [])
        if not office_ids:
            return Response({'error': 'No office IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count = Office.objects.filter(id__in=office_ids).delete()[0]
        return Response({'deleted_count': deleted_count})

    @swagger_auto_schema(
        operation_description="Bulk activate multiple offices",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'office_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            }
        ),
        responses={
            200: "Offices activated successfully",
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        """Bulk activate multiple offices"""
        office_ids = request.data.get('office_ids', [])
        if not office_ids:
            return Response({'error': 'No office IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        offices = Office.objects.filter(id__in=office_ids)
        activated_count = 0
        
        for office in offices:
            office.status = 'Active'
            office.updated_by = request.user
            office.save()
            activated_count += 1
        
        return Response({'activated_count': activated_count})

    @swagger_auto_schema(
        operation_description="Bulk deactivate multiple offices",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'office_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            }
        ),
        responses={
            200: "Offices deactivated successfully",
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        """Bulk deactivate multiple offices"""
        office_ids = request.data.get('office_ids', [])
        if not office_ids:
            return Response({'error': 'No office IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        offices = Office.objects.filter(id__in=office_ids)
        deactivated_count = 0
        
        for office in offices:
            office.status = 'Inactive'
            office.updated_by = request.user
            office.save()
            deactivated_count += 1
        
        return Response({'deactivated_count': deactivated_count})

    @action(detail=True, methods=['get'])
    def folders(self, request, pk=None):
        """Get folders for a specific office"""
        office = self.get_object()
        folders = OfficeFolder.objects.filter(office=office)
        serializer = OfficeFolderSerializer(folders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transfers(self, request, pk=None):
        """Get transfers for an office"""
        office = self.get_object()
        transfers = OfficeTransfer.objects.filter(source_office=office) | OfficeTransfer.objects.filter(destination_office=office)
        serializer = OfficeTransferSerializer(transfers, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get staff assigned to an office",
        responses={
            200: "List of staff members",
            404: "Office not found"
        }
    )
    @action(detail=True, methods=['get'])
    def staff(self, request, pk=None):
        """Get staff assigned to an office"""
        office = self.get_object()
        
        # For now, we're returning a placeholder implementation
        # In the future, this will query a Staff model that links users to offices
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Return a subset of users as a placeholder
        # In the real implementation, this would filter users by office assignment
        users = User.objects.filter(is_active=True)[:5]
        
        data = [{
            'id': str(user.id),
            'full_name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'role': 'Staff Member',  # Placeholder - would come from the office-user relationship
            'status': 'Active' if user.is_active else 'Inactive'
        } for user in users]
        
        return Response(data)
    
    @swagger_auto_schema(
        operation_description="Add a staff member to an office",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['user_id']
        ),
        responses={
            200: "Staff member added successfully",
            400: "Invalid request data",
            404: "Office or user not found"
        }
    )
    @action(detail=True, methods=['post'])
    def add_staff(self, request, pk=None):
        """Add a staff member to an office"""
        office = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'Staff Member')
        
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the user exists
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # In a real implementation, we would create/update a StaffAssignment model
        # For now, we'll just return success
        
        return Response({
            'success': True,
            'message': f'User {user.get_full_name()} has been assigned to {office.office_name} as {role}'
        })
    
    @swagger_auto_schema(
        operation_description="Remove a staff member from an office",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['user_id']
        ),
        responses={
            200: "Staff member removed successfully",
            400: "Invalid request data",
            404: "Office, user, or assignment not found"
        }
    )
    @action(detail=True, methods=['post'])
    def remove_staff(self, request, pk=None):
        """Remove a staff member from an office"""
        office = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the user exists
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # In a real implementation, we would delete the StaffAssignment record
        # For now, we'll just return success
        
        return Response({
            'success': True,
            'message': f'User {user.get_full_name()} has been removed from {office.office_name}'
        })


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
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

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
