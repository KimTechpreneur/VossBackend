from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Report, ReportTemplate
from .serializers import ReportSerializer, ReportTemplateSerializer

# Create your views here.

class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.filter(is_active=True)
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        report = self.get_object()
        if report.status in ['pending', 'processing']:
            return Response(
                {'error': 'Report is already being generated'},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.status = 'processing'
        report.save()

        # TODO: Implement actual report generation logic
        # This should be handled by a background task

        return Response({'status': 'Report generation started'})

    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        report = self.get_object()
        if not report.file:
            return Response(
                {'error': 'Report file not available'},
                status=status.HTTP_404_NOT_FOUND
            )

        # TODO: Implement file download logic
        return Response({'status': 'Download started'})
