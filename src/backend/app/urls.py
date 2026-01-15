from django.urls import path
from .views.uploadFolderView import UploadFolderView
from .views.auth import LoginView, SignupView
from .views.token import CustomTokenObtainPairView, CustomTokenRefreshView, TokenLogoutView
from .views.project_views import (
    ProjectsListView,
    ProjectDetailView,
    ProjectStatsView,
    RankedProjectsView,
    TopProjectsSummaryView,
)
from .views.user_views import UserMeView, PublicUserView, PasswordChangeView
from .views.resume_views import ResumeTemplatesView, ResumePreviewView, GenerateLatexResumeView

urlpatterns = [
    # Upload and analysis
    path("upload-folder/", UploadFolderView.as_view(), name="upload-folder"),
    
    # Projects endpoints
    path("projects/", ProjectsListView.as_view(), name="projects-list"),
    path("projects/stats/", ProjectStatsView.as_view(), name="projects-stats"),
    path("projects/ranked/", RankedProjectsView.as_view(), name="projects-ranked"),
    path("projects/ranked/summary/", TopProjectsSummaryView.as_view(), name="projects-ranked-summary"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="projects-detail"),

    # Resume endpoints
    path("resume/templates/", ResumeTemplatesView.as_view(), name="resume-templates"),
    path("resume/preview/", ResumePreviewView.as_view(), name="resume-preview"),
    path("resume/generate/latex/", GenerateLatexResumeView.as_view(), name="resume-generate-latex"),
    
    # Authentication
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    
    # JWT Token endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/logout/", TokenLogoutView.as_view(), name="token_logout"),
    
    # User profile endpoints
    path("users/me/", UserMeView.as_view(), name="user-me"),
    path("users/password/", PasswordChangeView.as_view(), name="user-password-change"),
    path("users/<str:username>/", PublicUserView.as_view(), name="user-public"),
]
