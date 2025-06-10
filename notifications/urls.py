from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationPreferenceViewSet,
    NotificationChannelViewSet,
    UserNotificationPreferenceViewSet,
    UserNotificationChannelViewSet,
    PersonalNotificationSettingsViewSet,
    NotificationHistoryItemViewSet,
    SystemNotificationRuleViewSet,
    NotificationTemplateViewSet
)

router = DefaultRouter()
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'channels', NotificationChannelViewSet, basename='notification-channel')
router.register(r'user-preferences', UserNotificationPreferenceViewSet, basename='user-notification-preference')
router.register(r'user-channels', UserNotificationChannelViewSet, basename='user-notification-channel')
router.register(r'settings', PersonalNotificationSettingsViewSet, basename='personal-notification-settings')
router.register(r'history', NotificationHistoryItemViewSet, basename='notification-history')
router.register(r'system-rules', SystemNotificationRuleViewSet, basename='system-notification-rule')
router.register(r'templates', NotificationTemplateViewSet, basename='notification-template')

urlpatterns = [
    path('', include(router.urls)),
] 