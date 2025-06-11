from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'agents'

router = DefaultRouter()
router.register(r'offices', views.OfficeViewSet)
router.register(r'', views.AgentViewSet, basename='agents')

urlpatterns = [
    path('', include(router.urls)),
] 