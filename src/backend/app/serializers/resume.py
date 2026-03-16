"""Resume template and generation serializers."""

from rest_framework import serializers


class ResumeTemplateSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()


class ResumeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=False, allow_blank=True)
    template_id = serializers.CharField(required=False, allow_blank=True)
    content = serializers.DictField()
    theme = serializers.CharField(required=False, allow_blank=True)
    rendercv_yaml = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ResumeGenerateRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, help_text="Optional saved resume name")
    template_id = serializers.CharField(required=False, allow_blank=True, help_text="Template ID to use")
    content = serializers.DictField(required=False, help_text="Resume content stored as JSON")
    theme = serializers.CharField(required=False, allow_blank=True, help_text="RenderCV theme for YAML/PDF generation")
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Optional list of project IDs to include"
    )
