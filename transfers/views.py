from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Avg
from drf_yasg.utils import swagger_auto_schema
from .models import Transfer, RoutingStep, TransferComment
from .serializers import (
    TransferSerializer, CreateTransferSerializer, BulkActionSerializer,
    ReassignAgentSerializer, ReturnRejectSerializer, RevisionRequestSerializer,
    TransferCommentSerializer
)
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.utils import create_and_send_notification

class TransferViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transfers.
    
    list:
    Return a list of all transfers.
    
    create:
    Create a new transfer.
    
    retrieve:
    Return the details of a specific transfer.
    
    update:
    Update all fields of a specific transfer.
    
    partial_update:
    Update one or more fields of a specific transfer.
    
    destroy:
    Delete a specific transfer.
    """
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'folder__title', 'agent__username', 'source_office__name', 'destination_office__name']
    ordering_fields = ['created_at', 'due_date', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransferSerializer
        return TransferSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = TransferSerializer(instance, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        date_from = self.request.query_params.get('dateRangeFrom')
        date_to = self.request.query_params.get('dateRangeTo')
        owning_unit = self.request.query_params.get('owningUnit')
        assigned_agent = self.request.query_params.get('assignedAgent')
        agent_id = self.request.query_params.get('agent_id')
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if owning_unit:
            queryset = queryset.filter(source_office__name=owning_unit)
        if assigned_agent:
            queryset = queryset.filter(agent__username=assigned_agent)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
            
        return queryset.select_related(
            'folder', 'source_office', 'destination_office',
            'agent', 'created_by', 'returned_by'
        ).prefetch_related('routing_steps')

    @swagger_auto_schema(
        operation_description="Get active transfers",
        responses={
            200: TransferSerializer(many=True),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        queryset = self.get_queryset().filter(status__in=['submitted', 'in_transit'])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get overdue transfers",
        responses={
            200: TransferSerializer(many=True),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        queryset = self.get_queryset().filter(
            status__in=['submitted', 'in_transit'],
            due_date__lt=timezone.now()
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get completed transfers",
        responses={
            200: TransferSerializer(many=True),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def completed(self, request):
        queryset = self.get_queryset().filter(status='delivered')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get draft transfers",
        responses={
            200: TransferSerializer(many=True),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def draft(self, request):
        queryset = self.get_queryset().filter(status='draft')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get returned transfers",
        responses={
            200: TransferSerializer(many=True),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def returned(self, request):
        queryset = self.get_queryset().filter(status__in=['returned', 'return_approved', 'return_rejected'])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get transfer history",
        responses={
            200: "Transfer history",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        transfer = self.get_object()
        return Response(transfer.history)

    @swagger_auto_schema(
        operation_description="Recall a transfer",
        responses={
            200: "Transfer recalled successfully",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def recall(self, request, pk=None):
        transfer = self.get_object()
        if not transfer.can_be_recalled():
            return Response(
                {"error": "Transfer cannot be recalled in its current state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transfer.status = 'recalled'
        transfer.save()
        return Response({'status': 'transfer recalled'})

    @swagger_auto_schema(
        operation_description="Escalate a transfer",
        responses={
            200: "Transfer escalated successfully",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        transfer = self.get_object()
        if not transfer.can_be_escalated():
            return Response(
                {"error": "Transfer cannot be escalated in its current state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transfer.status = 'escalated'
        transfer.save()
        return Response({'status': 'transfer escalated'})

    @swagger_auto_schema(
        operation_description="Reassign agent for a transfer",
        request_body=ReassignAgentSerializer,
        responses={
            200: TransferSerializer,
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def reassign_agent(self, request, pk=None):
        transfer = self.get_object()
        serializer = ReassignAgentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transfer.agent_id = serializer.validated_data['new_agent_id']
        if 'agent_notes' in serializer.validated_data:
            transfer.agent_notes = serializer.validated_data['agent_notes']
        transfer.save()
        
        return Response(self.get_serializer(transfer).data)

    @swagger_auto_schema(
        operation_description="Force return a transfer",
        responses={
            200: "Transfer force returned successfully",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def force_return(self, request, pk=None):
        transfer = self.get_object()
        if not transfer.can_be_returned():
            return Response(
                {"error": "Transfer cannot be returned in its current state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transfer.status = 'force_returned'
        transfer.returned_at = timezone.now()
        transfer.returned_by = request.user
        transfer.save()
        return Response({'status': 'transfer force returned'})

    @swagger_auto_schema(
        operation_description="Approve return of a transfer",
        responses={
            200: "Transfer return approved successfully",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def approve_return(self, request, pk=None):
        transfer = self.get_object()
        if not transfer.can_be_approved():
            return Response(
                {"error": "Transfer cannot be approved in its current state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transfer.status = 'return_approved'
        transfer.save()
        return Response({'status': 'transfer return approved'})

    @swagger_auto_schema(
        operation_description="Reject return of a transfer",
        request_body=ReturnRejectSerializer,
        responses={
            200: "Transfer return rejected successfully",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def reject_return(self, request, pk=None):
        transfer = self.get_object()
        if not transfer.can_be_rejected():
            return Response(
                {"error": "Transfer cannot be rejected in its current state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReturnRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transfer.status = 'return_rejected'
        transfer.return_reason = serializer.validated_data['reason']
        if 'comments' in serializer.validated_data:
            transfer.return_notes = serializer.validated_data['comments']
        transfer.save()
        
        return Response({'status': 'transfer return rejected'})

    @swagger_auto_schema(
        operation_description="Scan a transfer QR code",
        responses={
            200: "Transfer scanned successfully",
            404: "Transfer not found",
            400: "Invalid QR code or transfer status"
        }
    )
    @action(detail=True, methods=['post'])
    def scan(self, request, pk=None):
        """
        Handles the scanning of a transfer's QR code for pickup or delivery.
        """
        transfer = self.get_object()
        user = request.user

        # Agent pickup
        if transfer.status == 'submitted' and transfer.agent == user:
            transfer.status = 'in_transit'
            transfer.save()
            # Notify the creator that the agent has picked up the transfer
            create_and_send_notification(
                user=transfer.created_by,
                title="Transfer Picked Up",
                message=f"Agent {user.get_full_name()} has picked up transfer '{transfer.folder.title}'.",
                notification_type='transfer_update',
                reference_id=str(transfer.id)
            )
            return Response({'status': 'pickup_confirmed'})

        # Recipient delivery
        if transfer.status == 'in_transit' and transfer.destination_office in user.office_set.all():
            transfer.status = 'delivered'
            transfer.completed_at = timezone.now()
            transfer.save()
            # Notify the creator and agent that the transfer has been delivered
            create_and_send_notification(
                user=transfer.created_by,
                title="Transfer Delivered",
                message=f"Transfer '{transfer.folder.title}' has been successfully delivered to {transfer.destination_office.office_name}.",
                notification_type='transfer_update',
                reference_id=str(transfer.id)
            )
            if transfer.agent:
                create_and_send_notification(
                    user=transfer.agent,
                    title="Transfer Delivered",
                    message=f"Your assigned transfer '{transfer.folder.title}' has been delivered.",
                    notification_type='transfer_update',
                    reference_id=str(transfer.id)
                )
            return Response({'status': 'delivery_confirmed'})

        return Response(
            {"error": "This QR code is not valid for the current transfer status or user."},
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        operation_description="Request revision of a transfer",
        request_body=RevisionRequestSerializer,
        responses={
            200: "Transfer revision requested successfully",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def request_revision(self, request, pk=None):
        transfer = self.get_object()
        serializer = RevisionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transfer.status = 'revision_requested'
        transfer.return_notes = serializer.validated_data['comments']
        transfer.save()
        
        return Response({'status': 'transfer revision requested'})

    @swagger_auto_schema(
        operation_description="Bulk recall transfers",
        request_body=BulkActionSerializer,
        responses={
            200: "Transfers recalled successfully",
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_recall(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transfers = Transfer.objects.filter(
            id__in=serializer.validated_data['transfer_ids'],
            status__in=['submitted', 'in_transit']
        )
        
        for transfer in transfers:
            transfer.status = 'recalled'
            transfer.save()
        
        return Response({'status': 'transfers recalled'})

    @swagger_auto_schema(
        operation_description="Bulk escalate transfers",
        request_body=BulkActionSerializer,
        responses={
            200: "Transfers escalated successfully",
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_escalate(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transfers = Transfer.objects.filter(
            id__in=serializer.validated_data['transfer_ids'],
            status__in=['submitted', 'in_transit'],
            due_date__lt=timezone.now()
        )
        
        for transfer in transfers:
            transfer.status = 'escalated'
            transfer.save()
        
        return Response({'status': 'transfers escalated'})

    @swagger_auto_schema(
        operation_description="Bulk reassign agent",
        request_body=ReassignAgentSerializer,
        responses={
            200: "Agent reassigned successfully",
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_reassign_agent(self, request):
        serializer = ReassignAgentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transfers = Transfer.objects.filter(
            id__in=request.data.get('transfer_ids', []),
            delivery_method='agent'
        )
        
        for transfer in transfers:
            transfer.agent_id = serializer.validated_data['new_agent_id']
            if 'agent_notes' in serializer.validated_data:
                transfer.agent_notes = serializer.validated_data['agent_notes']
            transfer.save()
        
        return Response({'status': 'agent reassigned'})

    @swagger_auto_schema(
        operation_description="Bulk archive completed transfers",
        request_body=BulkActionSerializer,
        responses={
            200: "Transfers archived successfully",
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_archive(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transfers = Transfer.objects.filter(
            id__in=serializer.validated_data['transfer_ids'],
            status='delivered'
        )
        
        for transfer in transfers:
            transfer.status = 'archived'
            transfer.save()
        
        return Response({'status': 'transfers archived'})

    @swagger_auto_schema(
        operation_description="Bulk export transfers data",
        responses={
            200: "Transfer data exported successfully",
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['get'])
    def bulk_export(self, request):
        transfer_ids = request.query_params.getlist('transferIds', [])
        export_format = request.query_params.get('format', 'json')
        
        transfers = Transfer.objects.filter(id__in=transfer_ids)
        serializer = self.get_serializer(transfers, many=True)
        
        if export_format == 'csv':
            # Implement CSV export
            pass
        else:
            return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Bulk delete draft transfers",
        request_body=BulkActionSerializer,
        responses={
            204: "Transfers deleted successfully",
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['delete'])
    def bulk_delete_drafts(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        Transfer.objects.filter(
            id__in=serializer.validated_data['transfer_ids'],
            status='draft'
        ).delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Bulk submit draft transfers",
        request_body=BulkActionSerializer,
        responses={
            200: "Transfers submitted successfully",
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_submit_drafts(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transfers = Transfer.objects.filter(
            id__in=serializer.validated_data['transfer_ids'],
            status='draft'
        )
        
        for transfer in transfers:
            transfer.status = 'submitted'
            transfer.submitted_at = timezone.now()
            transfer.save()
        
        return Response({'status': 'transfers submitted'})

    @swagger_auto_schema(
        operation_description="Get summary metrics for all transfer types.",
        responses={200: "A JSON object with metrics for each transfer status."}
    )
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """
        Returns a dictionary of summary metrics for various transfer statuses.
        Accepts a 'scope' query parameter to limit the metrics returned.
        """
        scope = request.query_params.get('scope')
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = today_start - timezone.timedelta(days=now.weekday())
        start_of_last_week = start_of_week - timezone.timedelta(days=7)

        # Base querysets
        active_transfers = Transfer.objects.filter(status__in=['submitted', 'in_transit'])
        overdue_transfers = active_transfers.filter(due_date__lt=now)
        completed_transfers = Transfer.objects.filter(status='delivered')
        draft_transfers = Transfer.objects.filter(status='draft')
        returned_transfers = Transfer.objects.filter(status__in=['returned', 'return_approved', 'return_rejected'])

        metrics = {}

        if not scope or scope == 'active':
            metrics['active'] = {
                'totalActive': active_transfers.count(),
                'pickedUpToday': active_transfers.filter(routing_steps__status='completed', routing_steps__completed_at__gte=today_start).distinct().count(),
                'pickedUpThisWeek': active_transfers.filter(routing_steps__status='completed', routing_steps__completed_at__gte=start_of_week).distinct().count(),
                'pendingReceipt': active_transfers.filter(routing_steps__status='pending').distinct().count(),
                'overdue': overdue_transfers.count(),
                'trend': active_transfers.filter(created_at__gte=start_of_last_week).count() - active_transfers.filter(created_at__gte=start_of_week).count()
            }
        
        if not scope or scope == 'overdue':
            metrics['overdue'] = {
                'totalOverdue': overdue_transfers.count(),
                'overdueThreePlusDays': overdue_transfers.filter(due_date__lt=now - timezone.timedelta(days=3)).count(),
                'withAgentsNotDelivered': overdue_transfers.filter(delivery_method='agent').count(),
                'escalatedFiles': overdue_transfers.filter(status='escalated').count(),
                'trend': overdue_transfers.filter(created_at__gte=start_of_last_week).count() - overdue_transfers.filter(created_at__gte=start_of_week).count()
            }

        if not scope or scope == 'completed':
            metrics['completed'] = {
                'totalCompleted': completed_transfers.count(),
                'completedToday': completed_transfers.filter(completed_at__gte=today_start).count(),
                'completedThisWeek': completed_transfers.filter(completed_at__gte=start_of_week).count(),
                'averageRating': 0,
                'fastestDelivery': 'N/A' 
            }

        if not scope or scope == 'draft':
            metrics['draft'] = {
                'totalDrafts': draft_transfers.count(),
                'recentlyModified': draft_transfers.filter(updated_at__gte=now - timezone.timedelta(days=7)).count(),
                'oldDrafts': draft_transfers.filter(updated_at__lt=now - timezone.timedelta(days=30)).count(),
            }

        if not scope or scope == 'returns':
            metrics['returns'] = {
                'totalReturns': returned_transfers.count(),
                'pendingReview': returned_transfers.filter(status='returned').count(),
                'approvedToday': returned_transfers.filter(status='return_approved', updated_at__gte=today_start).count(),
                'rejectedToday': returned_transfers.filter(status='return_rejected', updated_at__gte=today_start).count(),
                'trend': returned_transfers.filter(created_at__gte=start_of_last_week).count() - returned_transfers.filter(created_at__gte=start_of_week).count()
            }
        
        if not scope or scope == 'history':
             metrics['history'] = {
                'totalTransfers': Transfer.objects.all().count(),
                'completedThisMonth': completed_transfers.filter(completed_at__gte=now.replace(day=1)).count(),
                'averageDuration': 'N/A',
                'successRate': (completed_transfers.count() / Transfer.objects.all().count() * 100) if Transfer.objects.all().count() > 0 else 0
            }
        
        return Response(metrics)

def mark_as_collected(request, transfer_id):
    transfer = Transfer.objects.get(id=transfer_id)
    transfer.status = 'collected'
    transfer.collected_by = request.user
    transfer.collected_at = timezone.now()
    transfer.save()

    # Broadcast the update
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'transfers',
        {
            'type': 'transfer_update',
            'data': {
                'id': transfer.id,
                'status': transfer.status,
                'collected_by': transfer.collected_by.email,
                'collected_at': transfer.collected_at.isoformat(),
                'action': 'mark_collected'
            }
        }
    )

class TransferCommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transfer comments.
    
    list:
    Return a list of all transfer comments.
    
    create:
    Create a new transfer comment.
    
    retrieve:
    Return the details of a specific transfer comment.
    
    update:
    Update all fields of a specific transfer comment.
    
    partial_update:
    Update one or more fields of a specific transfer comment.
    
    destroy:
    Delete a specific transfer comment.
    """
    queryset = TransferComment.objects.all()
    serializer_class = TransferCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        transfer_id = self.request.query_params.get('transfer_id', None)
        is_internal = self.request.query_params.get('is_internal', None)
        comment_type = self.request.query_params.get('comment_type', None)
        
        if transfer_id:
            queryset = queryset.filter(transfer_id=transfer_id)
        if is_internal is not None:
            queryset = queryset.filter(is_internal=is_internal.lower() == 'true')
        if comment_type:
            queryset = queryset.filter(comment_type=comment_type)
            
        return queryset.select_related('transfer', 'user', 'parent_comment')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
