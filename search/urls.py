from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransferPathStepViewSet,
    AgentActivityViewSet,
    TransferTrailViewSet,
    SearchFiltersViewSet,
    SearchResultItemViewSet,
    SearchHistoryViewSet,
    SearchResultViewSet,
    SearchFilterOptionsView
)

router = DefaultRouter()
router.register(r'transfer-path', TransferPathStepViewSet, basename='transfer-path')
router.register(r'agent-activity', AgentActivityViewSet, basename='agent-activity')
router.register(r'transfer-trail', TransferTrailViewSet, basename='transfer-trail')
router.register(r'filters', SearchFiltersViewSet, basename='search-filters')
router.register(r'results', SearchResultItemViewSet, basename='search-results')
router.register(r'history', SearchHistoryViewSet, basename='search-history')
router.register(r'search-results', SearchResultViewSet, basename='search-result')

urlpatterns = [
    path('filter-options/', SearchFilterOptionsView.as_view(), name='search-filter-options'),
    path('', include(router.urls)),
] 