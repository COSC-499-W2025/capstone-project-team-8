"""Project serializers for listing, detail views, and updates."""

from rest_framework import serializers


class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    classification = serializers.CharField()
    languages = serializers.ListField(child=serializers.CharField())
    frameworks = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField(read_only=True)
    last_updated = serializers.DateTimeField(read_only=True)
    thumbnail_url = serializers.URLField(allow_blank=True, required=False)


class ProjectDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    classification = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    last_updated = serializers.DateTimeField(read_only=True)
    thumbnail_url = serializers.URLField(allow_blank=True, required=False)
    contributors = serializers.ListField()
    languages = serializers.ListField()
    frameworks = serializers.ListField()
    files = serializers.ListField()


class ProjectUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    classification = serializers.CharField(required=False)


class ProjectStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_classification = serializers.DictField()


class ProjectConsentSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    consent = serializers.BooleanField()
