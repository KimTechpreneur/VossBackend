from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'transfers'

router = DefaultRouter()
router.register(r'transfers', views.TransferViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
    path('transfers/<uuid:transfer_id>/mark-collected/', views.mark_as_collected, name='mark_as_collected'),
] 