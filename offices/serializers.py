from rest_framework import serializers
from .models import (
    Office, ExternalOffice, InternalOffice, OfficeStaffMember,
    OfficeFolder, OfficeTransfer
)

class OfficeSerializer(serializers.ModelSerializer):
    ongoing_transfers = serializers.IntegerField(read_only=True)

    class Meta:
        model = Office
        fields = [
            'id', 'office_name', 'office_type', 'office_code',
            'head_of_office', 'staff_count', 'status', 'location',
            'description', 'created_date', 'last_updated_date',
            'updated_by', 'ongoing_transfers'
        ]
        read_only_fields = ['id', 'created_date', 'last_updated_date', 'ongoing_transfers']

class ExternalOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalOffice
        fields = [
            'id', 'office_name', 'office_type', 'office_code',
            'contact_person', 'contact_email', 'contact_phone',
            'status', 'location', 'description', 'created_date',
            'last_updated_date', 'updated_by'
        ]
        read_only_fields = ['id', 'created_date', 'last_updated_date']

class OfficeStaffMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeStaffMember
        fields = [
            'id', 'office', 'user', 'role', 'status',
            'assigned_date', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_date', 'updated_at']

class OfficeFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeFolder
        fields = [
            'id', 'office', 'folder_id', 'title', 'status',
            'date', 'initiated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class OfficeTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeTransfer
        fields = [
            'id', 'office', 'transfer_id', 'date', 'party',
            'status', 'subject', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class InternalOfficeSerializer(serializers.ModelSerializer):
    staff_members = OfficeStaffMemberSerializer(many=True, read_only=True)
    folders = OfficeFolderSerializer(many=True, read_only=True)
    transfers = OfficeTransferSerializer(many=True, read_only=True)
    ongoing_transfers = serializers.IntegerField(read_only=True)

    class Meta:
        model = InternalOffice
        fields = [
            'id', 'office_name', 'office_type', 'office_code',
            'head_of_office', 'staff_count', 'status', 'location',
            'description', 'created_date', 'last_updated_date',
            'updated_by', 'staff_members', 'folders', 'transfers',
            'ongoing_transfers'
        ]
        read_only_fields = ['id', 'created_date', 'last_updated_date', 'ongoing_transfers']

class OfficeBulkUpdateSerializer(serializers.Serializer):
    office_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    status = serializers.ChoiceField(
        choices=InternalOffice.STATUS_CHOICES,
        required=False
    )
    head_of_office = serializers.PrimaryKeyRelatedField(
        queryset='users.User.objects.all()',
        required=False
    )

    def validate(self, data):
        if not any([data.get('status'), data.get('head_of_office')]):
            raise serializers.ValidationError(
                "At least one of status or head_of_office must be provided"
            )
        return data 