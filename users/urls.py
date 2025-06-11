from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, RoleViewSet, PermissionViewSet,
    PasswordResetViewSet, UserProfileViewSet
)

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'password-resets', PasswordResetViewSet)

urlpatterns = [

    
    # User management endpoints
    path('', include(router.urls)),
    path('profile/', UserProfileViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update'
    }), name='user-profile'),

] 