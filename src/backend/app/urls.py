from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views.uploadFolderView import UploadFolderView
from .views.auth import LoginView, SignupView
from .views.token import CustomTokenObtainPairView, CustomTokenRefreshView, TokenLogoutView
from .views.project_views import (
    ProjectsListView,
    ProjectDetailView,
    ProjectStatsView,
    RankedProjectsView,
    TopProjectsSummaryView,
    ProjectThumbnailUploadView,
)
from .views.user_views import UserMeView, PublicUserView, PasswordChangeView, ProfileImageUploadView
from .views.resume_views import ResumeTemplatesView, ResumePreviewView, GenerateLatexResumeView
from .views.portfolio_views import (
    PortfolioListView,
    PortfolioGenerateView,
    PortfolioDetailView,
    PortfolioEditView,
    PortfolioAddProjectView,
    PortfolioRemoveProjectView,
    PortfolioReorderProjectsView
)
from .views.resume_views import (
    ResumeTemplatesView, 
    ResumePreviewView, 
    GenerateLatexResumeView,
    ResumeGenerateView,
    ResumeDetailView,
    ResumeEditView,
)
from .views.incremental_upload_views import (
    IncrementalUploadView,
    ProjectHistoryView,
    PortfolioIncrementalStatsView,
)

urlpatterns = [
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Upload and analysis
    path("upload-folder/", UploadFolderView.as_view(), name="upload-folder"),
    path("incremental-upload/", IncrementalUploadView.as_view(), name="incremental-upload"),
    
    # Projects endpoints
    path("projects/", ProjectsListView.as_view(), name="projects-list"),
    path("projects/stats/", ProjectStatsView.as_view(), name="projects-stats"),
    path("projects/ranked/", RankedProjectsView.as_view(), name="projects-ranked"),
    path("projects/ranked/summary/", TopProjectsSummaryView.as_view(), name="projects-ranked-summary"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="projects-detail"),
    path("projects/<int:project_id>/history/", ProjectHistoryView.as_view(), name="project-history"),

    # Portfolio endpoints
    path("portfolio/", PortfolioListView.as_view(), name="portfolio-list"),
    path("portfolio/generate/", PortfolioGenerateView.as_view(), name="portfolio-generate"),
    path("portfolio/<int:pk>/", PortfolioDetailView.as_view(), name="portfolio-detail"),
    path("portfolio/<int:pk>/edit/", PortfolioEditView.as_view(), name="portfolio-edit"),
    path("portfolio/<int:pk>/projects/add/", PortfolioAddProjectView.as_view(), name="portfolio-add-project"),
    path("portfolio/<int:pk>/projects/<int:project_id>/", PortfolioRemoveProjectView.as_view(), name="portfolio-remove-project"),
    path("portfolio/<int:pk>/projects/reorder/", PortfolioReorderProjectsView.as_view(), name="portfolio-reorder-projects"),
    path("portfolio/<int:portfolio_id>/incremental-stats/", PortfolioIncrementalStatsView.as_view(), name="portfolio-incremental-stats"),

    # Resume endpoints
    path("resume/templates/", ResumeTemplatesView.as_view(), name="resume-templates"),
    path("resume/preview/", ResumePreviewView.as_view(), name="resume-preview"),
    path("resume/generate/latex/", GenerateLatexResumeView.as_view(), name="resume-generate-latex"),
    path("resume/generate/", ResumeGenerateView.as_view(), name="resume-generate"),
    path("resume/<int:pk>/", ResumeDetailView.as_view(), name="resume-detail"),
    path("resume/<int:pk>/edit/", ResumeEditView.as_view(), name="resume-edit"),
    
    # Authentication
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    
    # JWT Token endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/logout/", TokenLogoutView.as_view(), name="token_logout"),
    
    # User profile endpoints
    path("users/me/", UserMeView.as_view(), name="user-me"),
    path("users/me/profile-image/", ProfileImageUploadView.as_view(), name="user-profile-image-upload"),
    path("users/password/", PasswordChangeView.as_view(), name="user-password-change"),
    path("users/<str:username>/", PublicUserView.as_view(), name="user-public"),
    
    # Project thumbnail endpoints
    path("projects/<int:pk>/thumbnail/", ProjectThumbnailUploadView.as_view(), name="project-thumbnail-upload"),
]
