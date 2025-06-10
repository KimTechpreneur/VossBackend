from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'agents'

router = DefaultRouter()
router.register(r'offices', views.BaseOfficeViewSet)
router.register(r'agents', views.AgentViewSet)
router.register(r'agents/(?P<agent_pk>[^/.]+)/deliveries', views.AgentDeliveryViewSet, basename='agent-deliveries')

urlpatterns = [
    path('', include(router.urls)),
] 