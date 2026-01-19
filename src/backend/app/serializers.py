# This is where we define our serializers for converting complex data types, 
# such as querysets and model instances, 
# into native Python datatypes that can then be easily rendered 
# into JSON, XML or other content types.

from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Unique username for the account")
    email = serializers.EmailField(required=True, help_text="User's email address")
    password = serializers.CharField(required=True, write_only=True, help_text="Password for the account")
    confirm_password = serializers.CharField(required=True, write_only=True, help_text="Password confirmation")
    github_username = serializers.CharField(required=False, allow_blank=True, help_text="Optional GitHub username")
    github_email = serializers.EmailField(required=False, allow_blank=True, help_text="Optional GitHub email")


class SignupResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    username = serializers.CharField(help_text="Username of the created account")
    github_username = serializers.CharField(help_text="GitHub username if provided")
    github_email = serializers.EmailField(help_text="GitHub email if provided")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Username")
    password = serializers.CharField(required=True, write_only=True, help_text="Password")


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    username = serializers.CharField(help_text="Authenticated username")


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Error message describing what went wrong")


# User Serializers
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


# Project Serializers
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


# Resume Serializers  
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


# Upload Serializers
class UploadFolderSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, help_text="ZIP file containing project folders")
    github_username = serializers.CharField(required=False, allow_blank=True, help_text="GitHub username for the projects")
    consent_scan = serializers.BooleanField(required=False, default=False, help_text="Consent to scan and analyze project files")
    consent_send_llm = serializers.BooleanField(required=False, default=False, help_text="Consent to send data to LLM for AI analysis")