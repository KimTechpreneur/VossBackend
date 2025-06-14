from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Folder, FolderFile, FolderTransfer, FolderService,
    FolderCategory, RetentionClass, FolderSignature,
    FolderWorkflowStep, FolderComment
)
from .serializers import (
    FolderSerializer, FolderFileSerializer, FolderTransferSerializer,
    FolderServiceSerializer, FolderCategorySerializer, RetentionClassSerializer,
    FolderSignatureSerializer, FolderWorkflowStepSerializer, FolderCommentSerializer,
    FolderBulkUpdateSerializer, FolderDetailSerializer
)
from users.permissions import IsAdminUser, IsOwnerOrAdmin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class FolderServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing folder services.
    
    list:
    Return a list of all folder services.
    
    retrieve:
    Return the details of a specific folder service.
    """
    queryset = FolderService.objects.all()
    serializer_class = FolderServiceSerializer
    permission_classes = [IsAuthenticated]

class FolderCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing folder categories.
    
    list:
    Return a list of all folder categories.
    
    create:
    Create a new folder category.
    
    retrieve:
    Return the details of a specific folder category.
    
    update:
    Update all fields of a specific folder category.
    
    partial_update:
    Update one or more fields of a specific folder category.
    
    destroy:
    Delete a specific folder category.
    """
    queryset = FolderCategory.objects.all()
    serializer_class = FolderCategorySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class RetentionClassViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing retention classes.
    
    list:
    Return a list of all retention classes.
    
    create:
    Create a new retention class.
    
    retrieve:
    Return the details of a specific retention class.
    
    update:
    Update all fields of a specific retention class.
    
    partial_update:
    Update one or more fields of a specific retention class.
    
    destroy:
    Delete a specific retention class.
    """
    queryset = RetentionClass.objects.all()
    serializer_class = RetentionClassSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class FolderFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing folder files.
    
    list:
    Return a list of all folder files.
    
    create:
    Create a new folder file.
    
    retrieve:
    Return the details of a specific folder file.
    
    update:
    Update all fields of a specific folder file.
    
    partial_update:
    Update one or more fields of a specific folder file.
    
    destroy:
    Delete a specific folder file.
    """
    queryset = FolderFile.objects.all()
    serializer_class = FolderFileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get('file')
        
        if not uploaded_file:
            # Handle case where no file is uploaded but the endpoint is hit
            # This might be considered a bad request, depending on API design
            return
            
        folder = serializer.validated_data.get('folder')
        
        if not folder:
            # This is a temporary file upload
            serializer.save(
                file=uploaded_file,
                uploaded_by=self.request.user,
                original_filename=uploaded_file.name,
                file_type=uploaded_file.content_type,
                file_size=uploaded_file.size,
                is_temporary=True
            )
        else:
            serializer.save(
                file=uploaded_file,
                uploaded_by=self.request.user,
                original_filename=uploaded_file.name,
                file_type=uploaded_file.content_type,
                file_size=uploaded_file.size
            )

    def get_queryset(self):
        queryset = super().get_queryset()
        folder_id = self.request.query_params.get('folder_id', None)
        file_type = self.request.query_params.get('file_type', None)
        is_archived = self.request.query_params.get('is_archived', None)
        
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')
            
        return queryset.select_related('folder')

    @swagger_auto_schema(
        operation_description="Archive a folder file",
        responses={
            200: "File archived successfully",
            404: "File not found"
        }
    )
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        file = self.get_object()
        file.is_archived = True
        file.save()
        return Response({'status': 'file archived'})

    @swagger_auto_schema(
        operation_description="Unarchive a folder file",
        responses={
            200: "File unarchived successfully",
            404: "File not found"
        }
    )
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        file = self.get_object()
        file.is_archived = False
        file.save()
        return Response({'status': 'file unarchived'})

class FolderSignatureViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing folder signatures.
    
    list:
    Return a list of all folder signatures.
    
    create:
    Create a new folder signature.
    
    retrieve:
    Return the details of a specific folder signature.
    
    update:
    Update all fields of a specific folder signature.
    
    partial_update:
    Update one or more fields of a specific folder signature.
    
    destroy:
    Delete a specific folder signature.
    """
    queryset = FolderSignature.objects.all()
    serializer_class = FolderSignatureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        folder_id = self.request.query_params.get('folder_id', None)
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        return queryset.select_related('folder', 'signer')

    @swagger_auto_schema(
        operation_description="Verify a folder signature",
        responses={
            200: "Signature verified successfully",
            404: "Signature not found"
        }
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        signature = self.get_object()
        signature.is_verified = True
        signature.save()
        return Response({'status': 'signature verified'})

class FolderWorkflowStepViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing folder workflow steps.
    
    list:
    Return a list of all folder workflow steps.
    
    create:
    Create a new folder workflow step.
    
    retrieve:
    Return the details of a specific folder workflow step.
    
    update:
    Update all fields of a specific folder workflow step.
    
    partial_update:
    Update one or more fields of a specific folder workflow step.
    
    destroy:
    Delete a specific folder workflow step.
    """
    queryset = FolderWorkflowStep.objects.all()
    serializer_class = FolderWorkflowStepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        folder_id = self.request.query_params.get('folder_id', None)
        status = self.request.query_params.get('status', None)
        
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.select_related('folder')

    @swagger_auto_schema(
        operation_description="Complete a workflow step",
        responses={
            200: "Step completed successfully",
            404: "Step not found"
        }
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        step = self.get_object()
        step.status = 'completed'
        step.save()
        return Response({'status': 'step completed'})

class FolderCommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing folder comments.
    
    list:
    Return a list of all folder comments.
    
    create:
    Create a new folder comment.
    
    retrieve:
    Return the details of a specific folder comment.
    
    update:
    Update all fields of a specific folder comment.
    
    partial_update:
    Update one or more fields of a specific folder comment.
    
    destroy:
    Delete a specific folder comment.
    """
    queryset = FolderComment.objects.all()
    serializer_class = FolderCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        folder_id = self.request.query_params.get('folder_id', None)
        is_internal = self.request.query_params.get('is_internal', None)
        
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        if is_internal is not None:
            queryset = queryset.filter(is_internal=is_internal.lower() == 'true')
            
        return queryset.select_related('folder', 'user')

class FolderTransferViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing folder transfers.
    
    list:
    Return a list of all folder transfers.
    
    create:
    Create a new folder transfer.
    
    retrieve:
    Return the details of a specific folder transfer.
    
    update:
    Update all fields of a specific folder transfer.
    
    partial_update:
    Update one or more fields of a specific folder transfer.
    
    destroy:
    Delete a specific folder transfer.
    """
    queryset = FolderTransfer.objects.all()
    serializer_class = FolderTransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        folder_id = self.request.query_params.get('folder_id', None)
        status = self.request.query_params.get('status', None)
        agent = self.request.query_params.get('agent', None)
        
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        if status:
            queryset = queryset.filter(status=status)
        if agent:
            queryset = queryset.filter(agent_id=agent)
            
        return queryset.select_related('folder', 'agent')

    @swagger_auto_schema(
        operation_description="Mark a transfer as delivered",
        responses={
            200: "Transfer marked as delivered successfully",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        transfer = self.get_object()
        transfer.status = 'delivered'
        transfer.save()
        return Response({'status': 'transfer marked as delivered'})

class FolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing folders.
    
    list:
    Return a list of all folders.
    
    create:
    Create a new folder.
    
    retrieve:
    Return the details of a specific folder.
    
    update:
    Update all fields of a specific folder.
    
    partial_update:
    Update one or more fields of a specific folder.
    
    destroy:
    Delete a specific folder.
    """
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optimized queryset for folders, pre-fetching related data
        and applying filters from query parameters.
        """
        queryset = Folder.objects.select_related(
            'service', 'category', 'retention_class', 
            'source_office', 'destination_office', 'current_office', 
            'created_by', 'last_modified_by', 'assigned_agent'
        ).all()

        # Filtering logic
        status = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        search = self.request.query_params.get('search', None)

        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if search:
            queryset = queryset.filter(subject__icontains=search)

        return queryset.order_by('-created_at')

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [permissions.IsAuthenticated()]
        # Use IsOwnerOrAdmin for retrieve, update, partial_update, destroy
        return [IsOwnerOrAdmin()]

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Return the history of a specific folder.
        """
        folder = self.get_object()
        history_data = []

        # Add creation event
        history_data.append({
            'timestamp': folder.created_at,
            'action': 'Created',
            'details': f'Folder "{folder.title}" was created.',
            'user': folder.created_by.get_full_name() if folder.created_by else 'System'
        })

        # Add last updated event
        if folder.updated_at and folder.updated_at != folder.created_at:
            history_data.append({
                'timestamp': folder.updated_at,
                'action': 'Updated',
                'details': 'Folder details were updated.',
                'user': 'System' # This would need a more sophisticated tracking mechanism
            })
        
        # This is a placeholder. You can expand this by querying related models
        # like FolderTransfer, FolderComment, etc., to build a comprehensive history.

        return Response({'history': history_data})

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Handles bulk updates for folders.
        """
        serializer = FolderBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_bulk_update(self, serializer):
        folder_ids = serializer.validated_data.get('folder_ids')
        update_data = {
            'status': serializer.validated_data.get('status'),
            'priority': serializer.validated_data.get('priority'),
            'service_id': serializer.validated_data.get('service_id'),
            'category_id': serializer.validated_data.get('category_id'),
            'source_office_id': serializer.validated_data.get('source_office_id'),
            'destination_office_id': serializer.validated_data.get('destination_office_id'),
            'assigned_agent_id': serializer.validated_data.get('assigned_agent_id'),
            'last_modified_by_id': self.request.user.id
        }
        for folder_id in folder_ids:
            folder = get_object_or_404(Folder, id=folder_id)
            for key, value in update_data.items():
                setattr(folder, key, value)
            folder.save()

    @swagger_auto_schema(
        operation_description="Mark a folder as completed",
        responses={
            200: "Folder completed successfully",
            404: "Folder not found"
        }
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        folder = self.get_object()
        folder.status = 'completed'
        folder.save()
        return Response({'status': 'folder completed'})

    @swagger_auto_schema(
        operation_description="Archive a folder",
        responses={
            200: "Folder archived successfully",
            404: "Folder not found"
        }
    )
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        folder = self.get_object()
        folder.status = 'archived'
        folder.save()
        return Response({'status': 'folder archived'})

def mark_as_collected(request, folder_id):
    folder = Folder.objects.get(id=folder_id)
    folder.status = 'collected'
    folder.collected_by = request.user
    folder.collected_at = timezone.now()
    folder.save()

    # Broadcast the update
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'folders',
        {
            'type': 'folder_update',
            'data': {
                'id': folder.id,
                'status': folder.status,
                'collected_by': folder.collected_by.email,
                'collected_at': folder.collected_at.isoformat(),
                'action': 'mark_collected'
            }
        }
    )
