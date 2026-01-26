"""Resume template and generation serializers."""

from rest_framework import serializers


class ResumeTemplateSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()


class ResumeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    template_id = serializers.CharField()
    content = serializers.DictField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ResumeGenerateRequestSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=True, help_text="Template ID to use")
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Optional list of project IDs to include"
    )
