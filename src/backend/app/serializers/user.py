"""User profile and account management serializers."""

from rest_framework import serializers


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Username")
    first_name = serializers.CharField(help_text="First name", allow_blank=True)
    last_name = serializers.CharField(help_text="Last name", allow_blank=True)
    email = serializers.EmailField(help_text="Email address")
    bio = serializers.CharField(help_text="User biography", allow_blank=True)
    github_username = serializers.CharField(help_text="GitHub username", allow_blank=True)
    linkedin_url = serializers.URLField(help_text="LinkedIn profile URL", allow_blank=True, required=False)
    portfolio_url = serializers.URLField(help_text="Portfolio website URL", allow_blank=True, required=False)
    twitter_username = serializers.CharField(help_text="Twitter username", allow_blank=True)
    profile_image_url = serializers.URLField(help_text="Profile image URL", allow_blank=True, required=False)
    university = serializers.CharField(help_text="University name", allow_blank=True)
    degree_major = serializers.CharField(help_text="Degree and major", allow_blank=True)
    education_city = serializers.CharField(help_text="Education city", allow_blank=True)
    education_state = serializers.CharField(help_text="Education state/province", allow_blank=True)
    expected_graduation = serializers.DateField(help_text="Expected graduation date", allow_null=True, required=False)
    date_joined = serializers.DateTimeField(help_text="Account creation date", required=False)


class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    github_username = serializers.CharField(required=False, allow_blank=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True)
    portfolio_url = serializers.URLField(required=False, allow_blank=True)
    twitter_username = serializers.CharField(required=False, allow_blank=True)
    university = serializers.CharField(required=False, allow_blank=True)
    degree_major = serializers.CharField(required=False, allow_blank=True)
    education_city = serializers.CharField(required=False, allow_blank=True)
    education_state = serializers.CharField(required=False, allow_blank=True)
    expected_graduation = serializers.DateField(required=False, allow_null=True)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True, help_text="Current password")
    new_password = serializers.CharField(required=True, write_only=True, help_text="New password")
    confirm_password = serializers.CharField(required=True, write_only=True, help_text="Confirm new password")


class PublicUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    bio = serializers.CharField(allow_blank=True)
    github_username = serializers.CharField(allow_blank=True)
    linkedin_url = serializers.URLField(allow_blank=True, required=False)
    portfolio_url = serializers.URLField(allow_blank=True, required=False)
    twitter_username = serializers.CharField(allow_blank=True)
    profile_image_url = serializers.URLField(allow_blank=True, required=False)
    university = serializers.CharField(allow_blank=True)
    degree_major = serializers.CharField(allow_blank=True)
    date_joined = serializers.DateTimeField(required=False)
