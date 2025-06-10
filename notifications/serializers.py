from rest_framework import serializers
from .models import (
    NotificationPreference, NotificationChannel,
    PersonalNotificationSettings, UserNotificationPreference,
    UserNotificationChannel, NotificationHistoryItem,
    SystemNotificationRule, NotificationTemplate, Notification, NotificationLog
)

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['id', 'title', 'description', 'is_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class NotificationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationChannel
        fields = ['id', 'label', 'is_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    preference = NotificationPreferenceSerializer()

    class Meta:
        model = UserNotificationPreference
        fields = ['id', 'user_settings', 'preference', 'is_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserNotificationChannelSerializer(serializers.ModelSerializer):
    channel = NotificationChannelSerializer()

    class Meta:
        model = UserNotificationChannel
        fields = ['id', 'user_settings', 'channel', 'is_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PersonalNotificationSettingsSerializer(serializers.ModelSerializer):
    preferences = UserNotificationPreferenceSerializer(source='usernotificationpreference_set', many=True)
    channels = UserNotificationChannelSerializer(source='usernotificationchannel_set', many=True)

    class Meta:
        model = PersonalNotificationSettings
        fields = ['id', 'user', 'preferences', 'channels', 'digest_frequency', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        preferences_data = validated_data.pop('usernotificationpreference_set', [])
        channels_data = validated_data.pop('usernotificationchannel_set', [])

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update preferences
        if preferences_data:
            for pref_data in preferences_data:
                preference = pref_data['preference']
                is_enabled = pref_data['is_enabled']
                UserNotificationPreference.objects.update_or_create(
                    user_settings=instance,
                    preference=preference,
                    defaults={'is_enabled': is_enabled}
                )

        # Update channels
        if channels_data:
            for channel_data in channels_data:
                channel = channel_data['channel']
                is_enabled = channel_data['is_enabled']
                UserNotificationChannel.objects.update_or_create(
                    user_settings=instance,
                    channel=channel,
                    defaults={'is_enabled': is_enabled}
                )

        return instance

class NotificationHistoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationHistoryItem
        fields = [
            'id', 'user', 'title', 'message', 'type', 'status',
            'reference_id', 'file_link', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class NotificationHistoryListSerializer(serializers.Serializer):
    items = NotificationHistoryItemSerializer(many=True)
    filters = serializers.DictField()
    current_page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_items = serializers.IntegerField()

class SystemNotificationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemNotificationRule
        fields = [
            'id', 'name', 'trigger_type', 'recipients',
            'threshold_value', 'threshold_unit', 'notification_channels',
            'message_template', 'is_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SystemRulesListSerializer(serializers.Serializer):
    rules = SystemNotificationRuleSerializer(many=True)

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'subject', 'body',
            'notification_type', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    template = NotificationTemplateSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'template', 'notification_type',
            'subject', 'message', 'priority', 'is_read',
            'read_at', 'created_at', 'updated_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'read_at']

class NotificationLogSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)

    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'delivery_method',
            'status', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class MarkNotificationsReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )

class NotificationBulkUpdateSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    status = serializers.ChoiceField(
        choices=NotificationHistoryItem.STATUS_CHOICES,
        required=False
    )
    is_enabled = serializers.BooleanField(required=False)

    def validate(self, data):
        if not any([data.get('status'), data.get('is_enabled') is not None]):
            raise serializers.ValidationError(
                "At least one of status or is_enabled must be provided"
            )
        return data 