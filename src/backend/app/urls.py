from django.urls import path
from .views import UploadFolderView

urlpatterns = [
    path("upload-folder/", UploadFolderView.as_view(), name="upload-folder"),
]
