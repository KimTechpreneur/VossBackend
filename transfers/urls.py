from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import TransferViewSet, TransferCommentViewSet

app_name = 'transfers'

router = DefaultRouter()
router.register(r'', TransferViewSet, basename='transfer')

comment_list = TransferCommentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
comment_detail = TransferCommentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('comments/', comment_list, name='transfer-comment-list'),
    path('comments/<uuid:pk>/', comment_detail, name='transfer-comment-detail'),
    path('<uuid:transfer_id>/mark-collected/', views.mark_as_collected, name='mark_as_collected'),
    path('', include(router.urls)),
]