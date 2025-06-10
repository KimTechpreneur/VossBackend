from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'offices'

router = DefaultRouter()
router.register(r'internal-offices', views.InternalOfficeViewSet, basename='internaloffice')
router.register(r'staff-members', views.OfficeStaffMemberViewSet, basename='officestaffmember')
router.register(r'folders', views.OfficeFolderViewSet, basename='officefolder')
router.register(r'transfers', views.OfficeTransferViewSet, basename='officetransfer')

urlpatterns = [
    path('', include(router.urls)),
] 