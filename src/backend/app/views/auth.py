
from app.models import User  # Custom User model
from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework.request import Request
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status as http_status
from django.template import engines
from rest_framework_simplejwt.tokens import RefreshToken


class SignupView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request: Request):
        # Check if request is JSON or form data
        is_json = request.content_type == 'application/json'

        # Get data from appropriate source
        data = request.data if is_json else request.POST

        try:
            username = data['username']
            email = data['email']
            password = data['password']
            confirm_password = data['confirm_password']
            github_username = data.get('github_username', '').strip()
        except KeyError as e:
            if is_json:
                return JsonResponse(
                    {"error": f"Missing required field: {str(e)}"},
                    status=http_status.HTTP_400_BAD_REQUEST
                )
            return HttpResponse(
                b"<html><h1>Missing required field</h1></html>",
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        if password == confirm_password:
            try:
                user = User.objects.create_user(
                    username,
                    email,
                    password,
                    github_username=github_username
                )
            except IntegrityError:
                if User.objects.filter(username=username).exists():
                    if is_json:
                        return JsonResponse(
                            {"error": "Username already taken"},
                            status=http_status.HTTP_400_BAD_REQUEST
                        )
                    return HttpResponse(
                        b"<html><h1>Username Taken</h1></html>",
                        status=http_status.HTTP_400_BAD_REQUEST,
                    )
                elif User.objects.filter(email=email).exists():
                    if is_json:
                        return JsonResponse(
                            {"error": "Account with this email already exists"},
                            status=http_status.HTTP_400_BAD_REQUEST
                        )
                    return HttpResponse(
                        b"<html><h1>Account with this email already exists</h1></html>",
                        status=http_status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    if is_json:
                        return JsonResponse(
                            {"error": "Server error"},
                            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                    return HttpResponse(
                        b"<html><h1>Server error</h1></html>",
                        status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            # For JSON requests, return JWT tokens
            if is_json:
                refresh = RefreshToken.for_user(user)
                return JsonResponse(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "username": username,
                        "github_username": user.github_username or "",
                    },
                    status=http_status.HTTP_201_CREATED
                )

            # For form requests, use session (backward compatible)
            request.session['username'] = username
            return HttpResponse(
                bytes(f"<html><h1>Signed up: {username}</h1></html>", encoding="utf-8"),
                status=http_status.HTTP_200_OK,
            )
        else:
            if is_json:
                return JsonResponse(
                    {"error": "Passwords do not match"},
                    status=http_status.HTTP_400_BAD_REQUEST
                )
            return HttpResponse(
                b"<html><h1>Invalid Request</h1></html>",
                status=http_status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request):
        """Return signupusage or HTML form."""

        usage = {
            "endpoint": "/api/signup/",
            "method": "POST",
            "field": "user name",
            "description": "Enter information to signup.",
        }

        accept = request.META.get("HTTP_ACCEPT", "")

        if "text/html" in accept:
            html = """
            <!DOCTYPE html>
            <html>
              <body>
                <h1>Signup</h1>
                <form method="post">
                  {% csrf_token %}
                  <label>Username</label>
                  <input type="text" name="username"/><br>
                  <label>Email</label>
                  <input type="email" name="email"/><br>
                  <label>Password</label>
                  <input type="password" name="password"/><br>
                  <label>Confirm Password</label>
                  <input type="password" name="confirm_password"/><br>
                  <button type="submit">signup</button><br>
                </form>
              </body>
            </html>
            """
            django_engine = engines["django"]
            template = django_engine.from_string(html)
            rendered_html = template.render({}, request)
            return HttpResponse(rendered_html)

        return JsonResponse({"usage": usage})


class LoginView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request: Request):
        # Check if request is JSON or form data
        is_json = request.content_type == 'application/json'

        # Get data from appropriate source
        data = request.data if is_json else request.POST

        try:
            username = data['username']
            password = data['password']
        except KeyError as e:
            if is_json:
                return JsonResponse(
                    {"error": f"Missing required field: {str(e)}"},
                    status=http_status.HTTP_400_BAD_REQUEST
                )
            return HttpResponse(
                b"<html><h1>Missing required field</h1></html>",
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            # For JSON requests, return JWT tokens
            if is_json:
                refresh = RefreshToken.for_user(user)
                return JsonResponse(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "username": username,
                    },
                    status=http_status.HTTP_200_OK
                )

            # For form requests, use session (backward compatible)
            request.session['username'] = username
            return HttpResponse(
                bytes(f"<html><h1>Logged in: {user}</h1></html>", encoding="utf-8"),
                status=http_status.HTTP_200_OK,
            )
        else:
            if is_json:
                return JsonResponse(
                    {"error": "Invalid username or password"},
                    status=http_status.HTTP_401_UNAUTHORIZED
                )
            return HttpResponse(
                bytes("<html><h1>Wrong username or password.</h1></html>", encoding="utf-8"),
                status=http_status.HTTP_401_UNAUTHORIZED,
            )

    def get(self, request):
        """Return signupusage or HTML form."""

        usage = {
            "endpoint": "/api/login/",
            "method": "POST",
            "field": "user name",
            "description": "Enter information to signup.",
        }

        accept = request.META.get("HTTP_ACCEPT", "")

        if "text/html" in accept:
            html = """
            <!DOCTYPE html>
            <html>
              <body>
                <h1>Login</h1>
                <form method="post">
                  {% csrf_token %}
                  <label>Username</label>
                  <input type="text" name="username"/><br>
                  <label>Password</label>
                  <input type="password" name="password"/><br>
                  <button type="submit">login</button><br>
                </form>
              </body>
            </html>
            """
            django_engine = engines["django"]
            template = django_engine.from_string(html)
            rendered_html = template.render({}, request)   # empty context, request needed for csrf/url tags
            return HttpResponse(rendered_html)

        return JsonResponse({"usage": usage})

