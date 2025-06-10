from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'metrics', views.DashboardMetricsViewSet, basename='dashboard-metrics')
router.register(r'notifications', views.NotificationItemViewSet, basename='notifications')
router.register(r'activities', views.ActivityItemViewSet, basename='activities')
router.register(r'overdue-units', views.OverdueUnitViewSet, basename='overdue-units')
router.register(r'audit', views.AuditItemViewSet, basename='audit')
router.register(r'health', views.HealthMetricViewSet, basename='health')
router.register(r'transfer-volume', views.TransferVolumeDataViewSet, basename='transfer-volume')
router.register(r'processing-time', views.ProcessingTimeDataViewSet, basename='processing-time')
router.register(r'agent-success', views.AgentSuccessDataViewSet, basename='agent-success')

app_name = 'dashboard'

urlpatterns = [
    path('', include(router.urls)),
] 