from django.urls import path
from .views.uploadFolderView import UploadFolderView
from .views.auth import LoginView, SignupView
from .views.token import CustomTokenObtainPairView, CustomTokenRefreshView, TokenLogoutView
from .views.project_views import UserProjectsView, ProjectDetailView, UserStatsView, TechnologyStatsView


urlpatterns = [
    # Upload and analysis
    path("upload-folder/", UploadFolderView.as_view(), name="upload-folder"),
    
    # User projects
    path("projects/", UserProjectsView.as_view(), name="user-projects"),
    path("projects/<int:project_id>/", ProjectDetailView.as_view(), name="project-detail"),
    path("stats/", UserStatsView.as_view(), name="user-stats"),
    
    # Platform statistics (public)
    path("platform-stats/", TechnologyStatsView.as_view(), name="platform-stats"),
    
    # Authentication
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    
    # JWT Token endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/logout/", TokenLogoutView.as_view(), name="token_logout"),
]
