from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import TransferViewSet, TransferCommentViewSet

app_name = 'transfers'

router = DefaultRouter()
router.register(r'', TransferViewSet, basename='transfer')
router.register(r'comments', TransferCommentViewSet, basename='transfer-comment')

urlpatterns = [
    path('', include(router.urls)),
            path('<uuid:transfer_id>/mark-collected/', views.mark_as_collected, name='mark_as_collected'),
] 