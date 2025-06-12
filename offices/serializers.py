from rest_framework import serializers
from .models import Office, OfficeFolder, OfficeTransfer
from users.serializers import UserSerializer

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
        ref_name = "Office"

class OfficeDetailSerializer(serializers.ModelSerializer):
    head_of_office = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
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
        ref_name = "OfficeDetail"

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