from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    NotificationPreference, NotificationChannel,
    PersonalNotificationSettings, UserNotificationPreference,
    UserNotificationChannel, NotificationHistoryItem,
    SystemNotificationRule, NotificationTemplate
)
from .serializers import (
    NotificationPreferenceSerializer, NotificationChannelSerializer,
    PersonalNotificationSettingsSerializer, UserNotificationPreferenceSerializer,
    UserNotificationChannelSerializer, NotificationHistoryItemSerializer,
    SystemNotificationRuleSerializer, NotificationBulkUpdateSerializer,
    NotificationTemplateSerializer
)
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminUser, IsOwnerOrAdmin

# Create your views here.

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notification preferences.
    
    list:
    Return a list of all notification preferences.
    
    create:
    Create a new notification preference.
    
    retrieve:
    Return the details of a specific notification preference.
    
    update:
    Update all fields of a specific notification preference.
    
    partial_update:
    Update one or more fields of a specific notification preference.
    
    destroy:
    Delete a specific notification preference.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return NotificationPreference.objects.none()
        return NotificationPreference.objects.all()

class NotificationChannelViewSet(viewsets.ModelViewSet):
    queryset = NotificationChannel.objects.all()
    serializer_class = NotificationChannelSerializer
    permission_classes = [IsAuthenticated]

class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserNotificationPreference.objects.all()
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserNotificationPreference.objects.none()
        return UserNotificationPreference.objects.filter(user_settings__user=self.request.user)

class UserNotificationChannelViewSet(viewsets.ModelViewSet):
    queryset = UserNotificationChannel.objects.all()
    serializer_class = UserNotificationChannelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserNotificationChannel.objects.none()
        return UserNotificationChannel.objects.filter(user_settings__user=self.request.user)

class PersonalNotificationSettingsViewSet(viewsets.ModelViewSet):
    queryset = PersonalNotificationSettings.objects.all()
    serializer_class = PersonalNotificationSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PersonalNotificationSettings.objects.none()
        return PersonalNotificationSettings.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationHistoryItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notification history items.
    
    list:
    Return a list of all notification history items.
    
    create:
    Create a new notification history item.
    
    retrieve:
    Return the details of a specific notification history item.
    
    update:
    Update all fields of a specific notification history item.
    
    partial_update:
    Update one or more fields of a specific notification history item.
    
    destroy:
    Delete a specific notification history item.
    """
    serializer_class = NotificationHistoryItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return NotificationHistoryItem.objects.none()
        user = self.request.user
        queryset = NotificationHistoryItem.objects.all()
        queryset = queryset.filter(user=user)
        return queryset

    @swagger_auto_schema(
        operation_description="Bulk update multiple notification history items",
        request_body=NotificationHistoryItemSerializer(many=True),
        responses={
            200: NotificationHistoryItemSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data)
    
    def perform_bulk_update(self, serializer):
        serializer.save()

    @swagger_auto_schema(
        operation_description="Mark a notification as read",
        responses={
            200: "Notification marked as read successfully",
            404: "Notification not found"
        }
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @swagger_auto_schema(
        operation_description="Mark a notification as unread",
        responses={
            200: "Notification marked as unread successfully",
            404: "Notification not found"
        }
    )
    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = False
        notification.save()
        return Response({'status': 'notification marked as unread'})

class SystemNotificationRuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing system notification rules.
    
    list:
    Return a list of all system notification rules.
    
    create:
    Create a new system notification rule.
    
    retrieve:
    Return the details of a specific system notification rule.
    
    update:
    Update all fields of a specific system notification rule.
    
    partial_update:
    Update one or more fields of a specific system notification rule.
    
    destroy:
    Delete a specific system notification rule.
    """
    queryset = SystemNotificationRule.objects.all()
    serializer_class = SystemNotificationRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        rule_type = self.request.query_params.get('type', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset

    @swagger_auto_schema(
        operation_description="Enable a system notification rule",
        responses={
            200: "Rule enabled successfully",
            404: "Rule not found"
        }
    )
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        rule = self.get_object()
        rule.is_active = True
        rule.save()
        return Response({'status': 'rule enabled'})

    @swagger_auto_schema(
        operation_description="Disable a system notification rule",
        responses={
            200: "Rule disabled successfully",
            404: "Rule not found"
        }
    )
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        rule = self.get_object()
        rule.is_active = False
        rule.save()
        return Response({'status': 'rule disabled'})

    @swagger_auto_schema(
        operation_description="Test a system notification rule",
        responses={
            200: "Rule tested successfully",
            404: "Rule not found"
        }
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        rule = self.get_object()
        # Implement rule testing logic
        return Response({'status': 'rule tested'})

class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notification templates.
    
    list:
    Return a list of all notification templates.
    
    create:
    Create a new notification template.
    
    retrieve:
    Return the details of a specific notification template.
    
    update:
    Update all fields of a specific notification template.
    
    partial_update:
    Update one or more fields of a specific notification template.
    
    destroy:
    Delete a specific notification template.
    """
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        template_type = self.request.query_params.get('type', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset
