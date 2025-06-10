from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnitViewSet, UnitOptionsViewSet

router = DefaultRouter()
router.register(r'', UnitViewSet, basename='unit')
router.register(r'options', UnitOptionsViewSet, basename='unit-options')

urlpatterns = [
    path('', include(router.urls)),
] 