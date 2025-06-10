from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'folders'

router = DefaultRouter()
router.register(r'folders', views.FolderViewSet, basename='folder')
router.register(r'files', views.FolderFileViewSet, basename='folderfile')
router.register(r'transfers', views.FolderTransferViewSet, basename='foldertransfer')
router.register(r'services', views.FolderServiceViewSet, basename='folderservice')
router.register(r'categories', views.FolderCategoryViewSet, basename='foldercategory')
router.register(r'retention-classes', views.RetentionClassViewSet, basename='retentionclass')
router.register(r'signatures', views.FolderSignatureViewSet, basename='foldersignature')
router.register(r'workflow-steps', views.FolderWorkflowStepViewSet, basename='folderworkflowstep')
router.register(r'comments', views.FolderCommentViewSet, basename='foldercomment')

urlpatterns = [
    path('', include(router.urls)),
    path('folders/<uuid:folder_id>/mark-collected/', views.mark_as_collected, name='mark_as_collected'),
] 