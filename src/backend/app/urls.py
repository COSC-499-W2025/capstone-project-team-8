from django.urls import path
from .views.uploadFolderView import UploadFolderView
from .views.auth import LoginView, SignupView


urlpatterns = [
    path("upload-folder/", UploadFolderView.as_view(), name="upload-folder"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
]
