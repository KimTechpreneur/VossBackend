from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfficeViewSet, OfficeFolderViewSet, OfficeTransferViewSet

app_name = 'offices'

router = DefaultRouter()
router.register(r'offices', OfficeViewSet)
router.register(r'folders', OfficeFolderViewSet)
router.register(r'transfers', OfficeTransferViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 