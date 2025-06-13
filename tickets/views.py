from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Ticket, TicketComment, TicketCategory
from .serializers import TicketSerializer, TicketCommentSerializer, TicketCategorySerializer
from django.db import models

# Create your views here.

class TicketCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Ticket Categories.
    """
    queryset = TicketCategory.objects.all()
    serializer_class = TicketCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('category', 'created_by', 'assigned_to').all()
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]  # Temporarily allow unauthenticated access for development
    pagination_class = None

    def get_queryset(self):
        # Check if this is a schema generation request
        if getattr(self, 'swagger_fake_view', False):
            return Ticket.objects.none()

        # If no filters are applied, return all tickets
        if not self.request.query_params:
            return Ticket.objects.all()
            
        user = self.request.user
        if user.is_anonymous:
            # For development: return all tickets when no user is authenticated
            return super().get_queryset()
            
        return super().get_queryset().filter(
            models.Q(created_by=user) | models.Q(assigned_to=user)
        ).distinct()

    def perform_create(self, serializer):
        # For development: handle anonymous users
        if self.request.user.is_anonymous:
            serializer.save(created_by=None)
        else:
            serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        
        if not assigned_to_id:
            return Response(
                {'error': 'assigned_to is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ticket.assigned_to_id = assigned_to_id
            ticket.save()
            return Response(TicketSerializer(ticket).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'resolved'
        ticket.resolved_at = timezone.now()
        ticket.save()
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.save()
        return Response(TicketSerializer(ticket).data)

class TicketCommentViewSet(viewsets.ModelViewSet):
    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer
    permission_classes = [AllowAny]  # Temporarily allow unauthenticated access for development
    pagination_class = None

    def get_queryset(self):
        # Check if this is a schema generation request
        if getattr(self, 'swagger_fake_view', False):
            return TicketComment.objects.none()
            
        return TicketComment.objects.filter(ticket_id=self.kwargs.get('ticket_pk'))

    def perform_create(self, serializer):
        ticket_id = self.kwargs['ticket_pk']
        # For development: handle anonymous users
        if self.request.user.is_anonymous:
            serializer.save(
                ticket_id=ticket_id,
                author=None
            )
        else:
            serializer.save(
                ticket_id=ticket_id,
                author=self.request.user
            )
