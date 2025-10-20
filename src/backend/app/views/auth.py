
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework.request import Request
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status as http_status
from django.template import engines


class SignupView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request: Request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            try:
                User.objects.create_user(username, email, password)
            except IntegrityError:
                return HttpResponse(
                        b"<html><h1>Username Taken</h1></html>",
                        status = http_status.HTTP_400_BAD_REQUEST,
                    )

            request.session['username'] = username
            return HttpResponse(
                    bytes(f"<html><h1>Signed up: {username}</h1></html>", encoding="utf-8"),
                    status = http_status.HTTP_200_OK,
                )
        else:
            return HttpResponse(
                    b"<html><h1>Invalid Request</h1></html>",
                status = http_status.HTTP_400_BAD_REQUEST,
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
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request: Request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            request.session['username'] = username
            return HttpResponse(
                    bytes(f"<html><h1>Logged in: {user}</h1></html>", encoding="utf-8"),
                    status = http_status.HTTP_200_OK,
                )
        else:
            return HttpResponse(
                    bytes("<html><h1>Wrong username or password.</h1></html>", encoding="utf-8"),
                    status = http_status.HTTP_401_UNAUTHORIZED,
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
                  <button type="submit">signup</button><br>
                </form>
              </body>
            </html>
            """
            django_engine = engines["django"]
            template = django_engine.from_string(html)
            rendered_html = template.render({}, request)   # empty context, request needed for csrf/url tags
            return HttpResponse(rendered_html)


        return JsonResponse({"usage": usage})

