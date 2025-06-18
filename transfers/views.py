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
from notifications.utils import create_and_send_notification, json_encode
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import User
from drf_yasg import openapi

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
        queryset = self.get_queryset().filter(
            status__in=['submitted', 'in_transit', 'revision_requested', 'escalated']
        )
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
        operation_description="Confirms that a transfer has been delivered.",
        responses={
            200: TransferSerializer(),
            400: "Transfer cannot be delivered at this stage.",
            403: "You are not authorized to confirm delivery for this transfer.",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def delivery(self, request, pk=None):
        """
        Confirms that a transfer has been delivered.
        """
        transfer = self.get_object()
        
        # Check if transfer can be delivered
        if transfer.status not in ['in_transit', 'escalated']:
            return Response(
                {"detail": "Transfer cannot be delivered at this stage."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the user's office through their unit
        user_office = None
        if request.user.unit:
            # Get the first office associated with the user's unit
            user_office = request.user.unit.offices.first()
        
        # Check if user is authorized
        is_authorized = False
        
        # For escalated transfers
        if transfer.status == 'escalated':
            is_authorized = (
                # User is the one the transfer was escalated to
                (transfer.escalated_to == request.user) or
                # Or user is in destination office and has appropriate permissions
                (user_office and user_office == transfer.destination_office and
                 request.user.has_perm('transfers.can_confirm_delivery'))
            )
        # For regular transfers
        else:
            is_authorized = (
                # User is in destination office and has appropriate permissions
                (user_office and user_office == transfer.destination_office and
                 request.user.has_perm('transfers.can_confirm_delivery')) or
                # Or user is the assigned agent
                (transfer.delivery_method == 'agent' and transfer.agent and transfer.agent.user == request.user)
            )
        
        if not is_authorized:
            return Response(
                {"detail": "You are not authorized to confirm delivery for this transfer."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            with transaction.atomic():
                # Update transfer status
                transfer.status = 'delivered'
                transfer.completed_at = timezone.now()
                transfer.save()

                # Create delivery comment
                TransferComment.objects.create(
                    transfer=transfer,
                    comment=f"Transfer delivered by {request.user.get_full_name()}",
                    comment_type='general',
                    user=request.user
                )

                # Prepare WebSocket notification data
                ws_data = {
                    'id': str(transfer.id),
                    'status': transfer.status,
                    'delivered_by': str(request.user.id),
                    'delivered_by_email': request.user.email,
                    'delivered_at': timezone.now().isoformat(),
                    'action': 'delivery'
                }

                # Broadcast via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'transfers',
                    {
                        'type': 'transfer_update',
                        'data': json_encode(ws_data)
                    }
                )

                # Notify relevant users
                # 1. Notify the transfer creator
                if transfer.created_by:
                    create_and_send_notification(
                        user=transfer.created_by,
                        title=f'Transfer Delivered: {str(transfer.id)}',
                        message=f'Your transfer has been delivered by {request.user.get_full_name()}',
                        notification_type='transfer_delivered',
                        reference_id=str(transfer.id)
                    )

                # 2. Notify the agent if it's an agent delivery
                if transfer.delivery_method == 'agent' and transfer.agent and transfer.agent.user:
                    create_and_send_notification(
                        user=transfer.agent.user,
                        title=f'Transfer Delivered: {str(transfer.id)}',
                        message=f'Transfer has been delivered by {request.user.get_full_name()}',
                        notification_type='transfer_delivered',
                        reference_id=str(transfer.id)
                    )

                # 3. Notify users in the source office
                exclude_ids = [transfer.created_by.id if transfer.created_by else None]
                if transfer.agent and transfer.agent.user:
                    exclude_ids.append(transfer.agent.user.id)
                
                source_users = User.objects.filter(unit=transfer.source_office.unit).exclude(
                    id__in=[id for id in exclude_ids if id is not None]
                ).distinct()

                for user in source_users:
                    create_and_send_notification(
                        user=user,
                        title=f'Transfer Delivered: {str(transfer.id)}',
                        message=f'Transfer has been delivered by {request.user.get_full_name()}',
                        notification_type='transfer_delivered',
                        reference_id=str(transfer.id)
                    )

                return Response({
                    'status': 'success',
                    'message': 'Transfer delivered successfully',
                    'transfer': TransferSerializer(transfer, context={'request': request}).data
                })

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Confirms that a transfer has been picked up.",
        responses={
            200: TransferSerializer(),
            400: "Transfer cannot be picked up at this stage.",
            403: "You are not authorized to confirm pickup for this transfer.",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def pickup(self, request, pk=None):
        """
        Confirms that a transfer has been picked up.
        """
        transfer = self.get_object()
        
        # Check if transfer can be picked up
        if transfer.status != 'submitted':
            return Response(
                {"detail": "Transfer cannot be picked up at this stage."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if the user is authorized to pick up the transfer
        is_creator = transfer.created_by == request.user
        is_agent = transfer.delivery_method == 'agent' and transfer.agent and transfer.agent.user == request.user
        
        if not (is_creator or is_agent):
            return Response(
                {"detail": "You are not authorized to confirm pickup for this transfer."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        with transaction.atomic():
            transfer.status = 'in_transit'
            transfer.save()
            
            # Record history
            transfer.history.append({
                'timestamp': timezone.now().isoformat(),
                'action': 'picked_up',
                'user_id': str(request.user.id)
            })
            transfer.save()
            
            # Send notification
            create_and_send_notification(
                user=transfer.created_by,
                title=f'Transfer Picked Up: {transfer.id}',
                message=f'Transfer {transfer.id} has been picked up by {request.user.get_full_name()}.',
                notification_type='transfer_picked_up',
                reference_id=str(transfer.id),
            )

        serializer = self.get_serializer(transfer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def request_revision(self, request, pk=None):
        transfer = self.get_object()
        serializer = RevisionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                transfer.status = 'revision_requested'
                transfer.return_notes = serializer.validated_data['comments']
                transfer.save()

                # Notify the transfer creator
                if transfer.created_by:
                    create_and_send_notification(
                        user=transfer.created_by,
                        title=f'Revision Requested: Transfer {transfer.id}',
                        message=f'A revision has been requested for your transfer {transfer.id}. Comments: {transfer.return_notes}',
                        notification_type='transfer_revision',
                        reference_id=str(transfer.id)
                    )

                # Notify source office users
                source_office_users = User.objects.filter(unit=transfer.source_office.unit)
                if source_office_users.exists():
                    for recipient in source_office_users:
                        if recipient != transfer.created_by:  # Don't send duplicate notifications
                            create_and_send_notification(
                                user=recipient,
                                title=f'Revision Requested: Transfer {transfer.id}',
                                message=f'A revision has been requested for transfer {transfer.id}. Comments: {transfer.return_notes}',
                                notification_type='transfer_revision',
                                reference_id=str(transfer.id)
                            )

                # Broadcast the update via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'transfers',
                    {
                        'type': 'transfer_update',
                        'data': json_encode({
                            'id': str(transfer.id),
                            'status': transfer.status,
                            'requested_by': request.user.email,
                            'requested_at': timezone.now().isoformat(),
                            'comments': transfer.return_notes,
                            'action': 'revision_requested'
                        })
                    }
                )

                return Response({
                    'status': 'transfer revision requested',
                    'message': 'Notifications sent to relevant users'
                })

        except Exception as e:
            return Response(
                {'error': f'Failed to request revision: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """
        Escalate a transfer to a higher level or specific user.
        """
        transfer = self.get_object()
        serializer = EscalationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Update transfer status
                transfer.status = 'escalated'
                if serializer.validated_data.get('escalated_to_id'):
                    transfer.escalated_to_id = serializer.validated_data['escalated_to_id']
                transfer.save()

                # Create escalation comment if reason provided
                if serializer.validated_data.get('reason'):
                    TransferComment.objects.create(
                        transfer=transfer,
                        comment=serializer.validated_data['reason'],
                        comment_type='escalation',
                        user=request.user
                    )

                # Prepare WebSocket notification data
                ws_data = {
                    'id': str(transfer.id),
                    'status': transfer.status,
                    'escalated_by': str(request.user.id),
                    'escalated_by_email': request.user.email,
                    'escalated_to': str(transfer.escalated_to.id) if transfer.escalated_to else None,
                    'escalated_at': timezone.now().isoformat(),
                    'reason': serializer.validated_data.get('reason'),
                    'action': 'escalate'
                }

                # Broadcast via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'transfers',
                    {
                        'type': 'transfer_update',
                        'data': json_encode(ws_data)
                    }
                )

                # Notify relevant users
                # 1. Notify the transfer creator
                if transfer.created_by:
                    create_and_send_notification(
                        user=transfer.created_by,
                        title=f'Transfer Escalated: {str(transfer.id)}',
                        message=f'Your transfer has been escalated{" - " + serializer.validated_data["reason"] if serializer.validated_data.get("reason") else ""}',
                        notification_type='transfer_escalated',
                        reference_id=str(transfer.id)
                    )

                # 2. Notify the escalated_to user if specified
                if transfer.escalated_to:
                    create_and_send_notification(
                        user=transfer.escalated_to,
                        title=f'Transfer Escalated to You: {str(transfer.id)}',
                        message=f'A transfer has been escalated to you{" - " + serializer.validated_data["reason"] if serializer.validated_data.get("reason") else ""}',
                        notification_type='transfer_escalated',
                        reference_id=str(transfer.id)
                    )

                # 3. Notify users in the destination office (except those already notified)
                destination_users = User.objects.filter(unit=transfer.destination_office.unit).exclude(
                    id__in=[transfer.created_by.id if transfer.created_by else None, 
                           transfer.escalated_to.id if transfer.escalated_to else None]
                ).distinct()

                for user in destination_users:
                    create_and_send_notification(
                        user=user,
                        title=f'Transfer Escalated: {str(transfer.id)}',
                        message=f'A transfer in your office has been escalated{" - " + serializer.validated_data["reason"] if serializer.validated_data.get("reason") else ""}',
                        notification_type='transfer_escalated',
                        reference_id=str(transfer.id)
                    )

                return Response({
                    'status': 'success',
                    'message': 'Transfer escalated successfully',
                    'transfer': TransferSerializer(transfer, context={'request': request}).data
                })

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Get archived transfers",
        responses={
            200: TransferSerializer(many=True),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def archive(self, request):
        """
        Returns a list of archived transfers.
        """
        queryset = self.get_queryset().filter(status='archived')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Force return a transfer after delivery.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['reason']
        ),
        responses={
            200: TransferSerializer(),
            400: "Transfer cannot be returned at this stage.",
            403: "You are not authorized to return this transfer.",
            404: "Transfer not found"
        }
    )
    @action(detail=True, methods=['post'])
    def force_return(self, request, pk=None):
        """
        Force return a transfer after delivery.
        """
        transfer = self.get_object()
        
        # Only delivered transfers can be force returned
        if transfer.status != 'delivered':
            return Response(
                {"detail": "Only delivered transfers can be force returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the user's office through their unit
        user_office = None
        if request.user.unit:
            user_office = request.user.unit.offices.first()
        
        # Check if user is authorized (must be in destination office)
        if not user_office or user_office != transfer.destination_office:
            return Response(
                {"detail": "Only users in the destination office can return a transfer."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            with transaction.atomic():
                # Update transfer status
                transfer.status = 'force_returned'
                transfer.return_reason = request.data.get('reason', '')
                transfer.returned_at = timezone.now()
                transfer.returned_by = request.user
                transfer.save()

                # Create return comment
                TransferComment.objects.create(
                    transfer=transfer,
                    comment=f"Transfer force returned. Reason: {transfer.return_reason}",
                    comment_type='return',
                    user=request.user
                )

                # Notify the transfer creator
                if transfer.created_by:
                    create_and_send_notification(
                        user=transfer.created_by,
                        title=f'Transfer Returned: {transfer.id}',
                        message=f'Your transfer has been returned. Reason: {transfer.return_reason}',
                        notification_type='transfer_returned',
                        reference_id=str(transfer.id)
                    )

                # Notify source office users
                source_office_users = User.objects.filter(unit=transfer.source_office.unit)
                for user in source_office_users:
                    if user != transfer.created_by:  # Don't send duplicate notifications
                        create_and_send_notification(
                            user=user,
                            title=f'Transfer Returned: {transfer.id}',
                            message=f'A transfer has been returned. Reason: {transfer.return_reason}',
                            notification_type='transfer_returned',
                            reference_id=str(transfer.id)
                        )

                # Broadcast via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'transfers',
                    {
                        'type': 'transfer_update',
                        'data': json_encode({
                            'id': str(transfer.id),
                            'status': transfer.status,
                            'returned_by': request.user.email,
                            'returned_at': transfer.returned_at.isoformat(),
                            'reason': transfer.return_reason,
                            'action': 'force_return'
                        })
                    }
                )

                return Response(self.get_serializer(transfer).data)

        except Exception as e:
            return Response(
                {'error': f'Failed to return transfer: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
                'id': str(transfer.id),
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
        transfer_id = self.request.query_params.get('transfer', None)
        is_internal = self.request.query_params.get('is_internal', None)
        comment_type = self.request.query_params.get('type', None)

        if transfer_id:
            queryset = queryset.filter(transfer_id=transfer_id)
        if is_internal is not None:
            queryset = queryset.filter(is_internal=is_internal.lower() == 'true')
        if comment_type:
            queryset = queryset.filter(comment_type=comment_type)

        return queryset.select_related('transfer', 'user', 'parent_comment').order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EscalationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
    escalated_to_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_escalated_to_id(self, value):
        if value:
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this ID does not exist.")
        return value
