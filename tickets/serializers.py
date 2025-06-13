from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ticket, TicketComment, TicketCategory

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        ref_name = 'TicketsUserSerializer'
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'name', 'display_name']

    def get_name(self, obj):
        """Return the full name if available, otherwise username"""
        return obj.get_full_name() or obj.username

    def get_display_name(self, obj):
        """Return a user-friendly display name"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        else:
            return obj.username

class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = ['id', 'name', 'description']

class TicketCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = TicketComment
        fields = [
            'id', 'ticket', 'author', 'content',
            'created_at', 'updated_at', 'is_internal', 'attachments'
        ]
        read_only_fields = ['ticket', 'author', 'created_at', 'updated_at']

class TicketSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category = TicketCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=TicketCategory.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'priority', 'priority_display',
            'status', 'status_display', 'created_by', 'assigned_to',
            'created_at', 'updated_at', 'resolved_at', 'category', 'category_id',
            'tags', 'attachments', 'comment_count'
        ]
        read_only_fields = [
            'created_by', 'created_at', 'updated_at',
            'resolved_at', 'comment_count'
        ]

    def get_comment_count(self, obj):
        return obj.comments.count() 