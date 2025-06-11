from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, Role, Permission, PasswordReset
from .serializers import (
    UserSerializer, RoleSerializer, PermissionSerializer,
    PasswordResetSerializer, UserBulkUpdateSerializer, UserProfileSerializer,
    UserCreateSerializer, UserUpdateSerializer, TokenVerificationSerializer,
    PasswordResetConfirmSerializer
)
from .permissions import IsAdminUser, IsUnitHead, CanManageUsers, IsOwnerOrAdmin
from .filters import UserFilter
from .pagination import StandardResultsSetPagination
from .utils import (
    generate_secure_password, generate_reset_token,
    send_password_reset_email, send_user_invitation_email,
    validate_password_strength
)
from django.conf import settings
from datetime import timedelta, datetime

User = get_user_model()

# Create your views here.

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        module = self.request.query_params.get('module', None)
        if module:
            queryset = queryset.filter(module=module)
        return queryset

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status', None)
        role_type = self.request.query_params.get('type', None)
        
        if status:
            queryset = queryset.filter(status=status)
        if role_type:
            queryset = queryset.filter(type=role_type)
            
        return queryset

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        role = self.get_object()
        if role.is_locked:
            return Response(
                {'error': 'Cannot deactivate a locked role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        role.status = 'inactive'
        role.save()
        return Response({'status': 'role deactivated'})

    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        serializer = UserBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            role_ids = serializer.validated_data['role_ids']
            roles = Role.objects.filter(id__in=role_ids, is_locked=False)
            roles.update(status='inactive')
            return Response({'status': 'roles deactivated'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data)
    
    def perform_bulk_update(self, serializer):
        serializer.save()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    
    list:
    Return a list of all users.
    
    create:
    Create a new user.
    
    retrieve:
    Return the details of a specific user.
    
    update:
    Update all fields of a specific user.
    
    partial_update:
    Update one or more fields of a specific user.
    
    destroy:
    Delete a specific user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'employee_id']
    ordering_fields = ['first_name', 'last_name', 'email', 'role', 'status', 'department', 'last_login']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['create', 'request_password_reset', 'reset_password']:
            return [permissions.AllowAny()]
        elif self.action in ['destroy', 'bulk_update', 'bulk_deactivate', 'bulk_password_reset', 'bulk_role_change']:
            return [IsAdminUser()]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(id=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Handle password setup method
        password_method = request.data.get('passwordMethod', 'invite')
        temporary_password = None
        
        if password_method == 'manual':
            temporary_password = request.data.get('temporaryPassword')
            if not temporary_password:
                return Response(
                    {'error': 'Temporary password is required for manual setup'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            is_valid, error_message = validate_password_strength(temporary_password)
            if not is_valid:
                return Response(
                    {'error': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:  # invite
            temporary_password = generate_secure_password()
        
        # Create user with temporary password
        user = serializer.save()
        user.set_password(temporary_password)
        user.save()
        
        # Generate setup URL
        token = generate_reset_token()
        expiry = timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
        
        PasswordReset.objects.create(
            user=user,
            token=token,
            expires_at=expiry
        )
        
        setup_url = f"{settings.FRONTEND_URL}/setup-account?token={token}"
        
        # Send invitation email
        send_user_invitation_email(user, setup_url, temporary_password)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def request_password_reset(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            return Response(
                {'message': 'If an account exists with this email, you will receive password reset instructions.'},
                status=status.HTTP_200_OK
            )
        
        # Generate reset token
        token = generate_reset_token()
        expiry = timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
        
        # Create or update password reset record
        PasswordReset.objects.filter(user=user).delete()  # Invalidate any existing tokens
        PasswordReset.objects.create(
            user=user,
            token=token,
            expires_at=expiry
        )
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        send_password_reset_email(user, reset_url)
        
        return Response(
            {'message': 'If an account exists with this email, you will receive password reset instructions.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        token = request.data.get('token')
        new_password = request.data.get('newPassword')
        
        if not token or not new_password:
            return Response(
                {'error': 'Token and new password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reset = PasswordReset.objects.get(
                token=token,
                expires_at__gt=timezone.now(),
                is_used=False
            )
        except PasswordReset.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password strength
        is_valid, error_message = validate_password_strength(new_password)
        if not is_valid:
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update user's password
        user = reset.user
        user.set_password(new_password)
        user.force_password_change = False
        user.save()
        
        # Mark token as used
        reset.is_used = True
        reset.save()
        
        return Response(
            {'message': 'Password has been reset successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')
        
        if not current_password or not new_password:
            return Response(
                {'error': 'Current password and new password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify current password
        if not request.user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate new password strength
        is_valid, error_message = validate_password_strength(new_password)
        if not is_valid:
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        request.user.set_password(new_password)
        request.user.force_password_change = False
        request.user.save()
        
        return Response(
            {'message': 'Password has been changed successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Returns statistics about users.
        """
        total_users = User.objects.count()
        active_users = User.objects.filter(status='Active').count()
        inactive_users = User.objects.filter(status='Inactive').count()
        
        try:
            agents = User.objects.filter(role__name='Agent').count()
        except Exception:
            agents = 0

        try:
            unit_heads = User.objects.filter(role__name='Unit Head').count()
        except Exception:
            unit_heads = 0
        
        # Calculate monthly growth
        last_month = timezone.now() - timedelta(days=30)
        monthly_growth = User.objects.filter(created_at__gte=last_month).count()

        stats_data = {
            'totalUsers': total_users,
            'activeUsers': active_users,
            'inactiveUsers': inactive_users,
            'agents': agents,
            'unitHeads': unit_heads,
            'monthlyGrowth': monthly_growth
        }
        
        return Response(stats_data)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {'error': 'refresh_token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            print(f"Logout error: {str(e)}")  # For debugging
            return Response(
                {'error': 'Invalid token or logout failed'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        serializer = UserBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            users = User.objects.filter(id__in=user_ids)
            
            # Check permissions for each user
            for user in users:
                if not self.request.user.has_perm('users.can_deactivate_user', user):
                    return Response(
                        {'error': f'Not authorized to deactivate user {user.id}'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            users.update(
                status='Inactive',
                updated_at=timezone.now(),
                updated_by=self.request.user
            )
            
            # Log the bulk action
            self.log_bulk_action('deactivate', user_ids)
            
            return Response({'status': 'users deactivated'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_password_reset(self, request):
        serializer = UserBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            users = User.objects.filter(id__in=user_ids)
            
            # Check permissions for each user
            for user in users:
                if not self.request.user.has_perm('users.can_reset_password', user):
                    return Response(
                        {'error': f'Not authorized to reset password for user {user.id}'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            for user in users:
                user.force_password_change = True
                user.save()
                # Send password reset email
                self.send_password_reset_email(user)
            
            # Log the bulk action
            self.log_bulk_action('password_reset', user_ids)
            
            return Response({'status': 'password reset requested'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_role_change(self, request):
        serializer = UserBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            role = serializer.validated_data.get('role')
            
            if not role:
                return Response(
                    {'error': 'role is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            users = User.objects.filter(id__in=user_ids)
            
            # Check permissions for each user
            for user in users:
                if not self.request.user.has_perm('users.can_change_role', user):
                    return Response(
                        {'error': f'Not authorized to change role for user {user.id}'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            users.update(
                role=role,
                updated_at=timezone.now(),
            )
            
            # Log the bulk action
            self.log_bulk_action('role_change', user_ids)
            
            return Response({'status': 'roles updated'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_message(self, request):
        user_ids = request.data.get('user_ids')
        message = request.data.get('message')

        if not user_ids or not message:
            return Response(
                {'error': 'user_ids and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(id__in=user_ids)
        # In a real app, this would queue emails to be sent
        # For now, this is a placeholder
        print(f"Sending message '{message}' to users: {[user.email for user in users]}")
            
        return Response({'status': f'Message sent to {len(user_ids)} users.'})

    def log_bulk_action(self, action, user_ids):
        # Implement bulk action logging
        pass

    def send_password_reset_email(self, user):
        # Implement password reset email sending
        pass

class PasswordResetViewSet(viewsets.ModelViewSet):
    queryset = PasswordReset.objects.all()
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_permissions(self):
        if self.action in ['create', 'verify', 'confirm']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        serializer = TokenVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Token is valid."})
    
    @action(detail=False, methods=['post'])
    def confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."})

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_object(self):
        return self.request.user
