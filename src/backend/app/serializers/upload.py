"""File upload serializers for project imports."""

from rest_framework import serializers


class UploadFolderSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, help_text="ZIP file containing project folders")
    github_username = serializers.CharField(required=False, allow_blank=True, help_text="GitHub username for the projects")
    consent_scan = serializers.BooleanField(required=False, default=False, help_text="Consent to scan and analyze project files")
    consent_send_llm = serializers.BooleanField(required=False, default=False, help_text="Consent to send data to LLM for AI analysis")
