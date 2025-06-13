from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Role, Permission, PasswordReset

User = get_user_model()

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'module', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        source='permissions'
    )
    users_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'type', 'status', 'permissions', 'permission_ids',
            'color', 'is_locked', 'created_at', 'last_modified', 'users_count'
        ]
        read_only_fields = ['id', 'created_at', 'last_modified', 'users_count']

    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions', [])
        role = super().create(validated_data)
        
        if permissions_data:
            # Validate that all permission IDs exist
            permission_objects = Permission.objects.filter(id__in=permissions_data)
            if len(permission_objects) != len(permissions_data):
                missing_ids = set(permissions_data) - set(permission_objects.values_list('id', flat=True))
                raise serializers.ValidationError(f"Invalid permission IDs: {missing_ids}")
            
            role.permissions.set(permission_objects)
        
        return role

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions', None)
        role = super().update(instance, validated_data)
        
        if permissions_data is not None:
            # Validate that all permission IDs exist
            permission_objects = Permission.objects.filter(id__in=permissions_data)
            if len(permission_objects) != len(permissions_data):
                missing_ids = set(permissions_data) - set(permission_objects.values_list('id', flat=True))
                raise serializers.ValidationError(f"Invalid permission IDs: {missing_ids}")
            
            role.permissions.set(permission_objects)
        
        return role

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        write_only=True,
        source='role'
    )
    initials = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        ref_name = 'UsersUserSerializer'
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'role', 'role_id',
            'status', 'unit', 'voss_id', 'office_location',
            'notes', 'last_login', 'force_password_change', 'initials',
            'created_at', 'updated_at', 'password'
        ]
        read_only_fields = [
            'id', 'last_login', 'created_at', 'updated_at',
            'initials'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class UserCreateSerializer(serializers.ModelSerializer):
    passwordMethod = serializers.ChoiceField(
        choices=['invite', 'manual'],
        default='invite',
        write_only=True
    )
    temporaryPassword = serializers.CharField(
        required=False,
        write_only=True,
        min_length=8,
        allow_blank=True
    )
    forcePasswordChange = serializers.BooleanField(
        default=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'role', 'unit', 'office_location',
            'passwordMethod', 'temporaryPassword', 'forcePasswordChange'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        password_method = data.get('passwordMethod')
        temporary_password = data.get('temporaryPassword')

        if password_method == 'manual' and not temporary_password:
            raise serializers.ValidationError(
                {'temporaryPassword': 'Temporary password is required for manual setup'}
            )

        return data

    def create(self, validated_data):
        # Remove the extra fields that aren't in the User model
        password_method = validated_data.pop('passwordMethod')
        force_password_change = validated_data.pop('forcePasswordChange')
        temporary_password = validated_data.pop('temporaryPassword', None)

        # Create the user
        user = super().create(validated_data)

        # Set the password
        if password_method == 'manual':
            user.set_password(temporary_password)
        else:  # invite
            from .utils import generate_secure_password
            temp_password = generate_secure_password()
            user.set_password(temp_password)
            temporary_password = temp_password

        # Set force password change
        user.force_password_change = force_password_change
        user.save()

        # Generate setup URL and send invitation email
        from .utils import generate_reset_token, send_user_invitation_email
        from django.utils import timezone
        from django.conf import settings
        from datetime import timedelta

        token = generate_reset_token()
        expiry = timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
        
        from .models import PasswordReset
        PasswordReset.objects.create(
            user=user,
            token=token,
            expires_at=expiry
        )
        
        setup_url = f"{settings.FRONTEND_URL}/setup-account?token={token}"
        send_user_invitation_email(user, setup_url, temporary_password)

        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_active', 'role', 'phone', 'office_location', 'status', 'unit']
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
            'office_location': {'required': False}
        }

class PasswordResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordReset
        fields = ['id', 'user', 'token', 'created_at', 'expires_at', 'is_used']
        read_only_fields = ['id', 'token', 'created_at', 'expires_at', 'is_used']

class TokenVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        from django.utils import timezone
        from .models import PasswordReset
        
        try:
            reset = PasswordReset.objects.get(
                token=value,
                expires_at__gt=timezone.now(),
                is_used=False
            )
            self.context['reset'] = reset
            return value
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token.")

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True, min_length=8)

    def validate_token(self, value):
        from django.utils import timezone
        from .models import PasswordReset
        
        try:
            reset = PasswordReset.objects.get(
                token=value,
                expires_at__gt=timezone.now(),
                is_used=False
            )
            self.context['reset'] = reset
            return value
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token.")

    def validate_newPassword(self, value):
        from .utils import validate_password_strength
        
        is_valid, error_message = validate_password_strength(value)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value

    def save(self):
        reset = self.context['reset']
        new_password = self.validated_data['newPassword']
        
        # Update user's password
        user = reset.user
        user.set_password(new_password)
        user.force_password_change = False
        user.save()
        
        # Mark token as used
        reset.is_used = True
        reset.save()
        
        return user

class UserBulkUpdateSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    role = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Role.objects.all(),
        required=False
    )
    status = serializers.ChoiceField(
        choices=[
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
            ('Suspended', 'Suspended'),
        ],
        required=False
    )
    department = serializers.ChoiceField(
        choices=[
            ('Engineering Department', 'Engineering Department'),
            ('IT Department', 'IT Department'),
            ('Finance Department', 'Finance Department'),
            ('Student Affairs', 'Student Affairs'),
            ('Science Department', 'Science Department'),
            ('Library', 'Library'),
            ('Admissions', 'Admissions'),
        ],
        required=False
    )

    def validate(self, data):
        if not any([data.get('role'), data.get('status'), data.get('department')]):
            raise serializers.ValidationError(
                "At least one of role, status, or department must be provided"
            )
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    initials = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'role',
            'status', 'voss_id', 'office_location',
            'notes', 'last_login', 'initials', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'role', 'status', 'last_login',
            'created_at', 'updated_at', 'initials'
        ] 