from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import TicketViewSet, TicketCommentViewSet, TicketCategoryViewSet

app_name = 'tickets'

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'categories', TicketCategoryViewSet)

tickets_router = routers.NestedDefaultRouter(router, r'tickets', lookup='ticket')
tickets_router.register(r'comments', TicketCommentViewSet, basename='ticket-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tickets_router.urls)),
] 