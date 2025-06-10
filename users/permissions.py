from rest_framework import permissions

class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    Custom permission to only allow authenticated and active users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsUnitHead(permissions.BasePermission):
    """
    Allows access only to unit heads.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role.name == 'Unit Head'

class CanManageUsers(permissions.BasePermission):
    """
    Allows access to users who can manage other users.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or
            request.user.role.name == 'Unit Head'
        )

    def has_object_permission(self, request, view, obj):
        # Admin can manage all users
        if request.user.is_staff:
            return True

        # Unit Head can only manage users in their department
        if request.user.role.name == 'Unit Head':
            return obj.department == request.user.department

        return False

class CanDeactivateUser(permissions.BasePermission):
    """
    Allows access to users who can deactivate other users.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or
            request.user.role.name == 'Unit Head'
        )

    def has_object_permission(self, request, view, obj):
        # Admin can deactivate any user
        if request.user.is_staff:
            return True

        # Unit Head can only deactivate users in their department
        if request.user.role.name == 'Unit Head':
            return obj.department == request.user.department

        return False

class CanResetPassword(permissions.BasePermission):
    """
    Allows access to users who can reset passwords.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or
            request.user.role.name == 'Unit Head'
        )

    def has_object_permission(self, request, view, obj):
        # Admin can reset any user's password
        if request.user.is_staff:
            return True

        # Unit Head can only reset passwords for users in their department
        if request.user.role.name == 'Unit Head':
            return obj.department == request.user.department

        return False

class CanChangeRole(permissions.BasePermission):
    """
    Allows access to users who can change roles.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Only admin can change roles
        return request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.is_staff:
            return True
        
        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object is the user itself
        return obj == request.user 

    def has_permission(self, request, view):
        # Allow any authenticated user to access their own profile
        return request.user and request.user.is_authenticated

class IsAgentManager(permissions.BasePermission):
    """
    Allows access to users who are staff or have the role 'Agent Manager'.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or
            (hasattr(request.user, 'role') and getattr(request.user.role, 'name', None) == 'Agent Manager')
        )

    def has_object_permission(self, request, view, obj):
        # Staff can access any object
        if request.user.is_staff:
            return True
        # Agent Manager can access if they are assigned to the object (customize as needed)
        if hasattr(request.user, 'role') and getattr(request.user.role, 'name', None) == 'Agent Manager':
            # If the object has a user or agent field, check ownership/assignment
            if hasattr(obj, 'user'):
                return obj.user == request.user
            if hasattr(obj, 'agent_manager'):
                return obj.agent_manager == request.user
        return False 