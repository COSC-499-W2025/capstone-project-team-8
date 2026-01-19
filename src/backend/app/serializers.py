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