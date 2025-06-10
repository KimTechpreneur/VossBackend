from rest_framework import serializers
from .models import Ticket, TicketComment

class TicketCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TicketComment
        fields = [
            'id', 'ticket', 'author', 'content',
            'created_at', 'updated_at', 'is_internal', 'attachments'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

class TicketSerializer(serializers.ModelSerializer):
    comments = TicketCommentSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'priority', 'priority_display',
            'status', 'status_display', 'created_by', 'assigned_to',
            'created_at', 'updated_at', 'resolved_at', 'category',
            'tags', 'attachments', 'comments'
        ]
        read_only_fields = [
            'created_by', 'created_at', 'updated_at',
            'resolved_at', 'comments'
        ] 