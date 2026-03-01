# Import all serializers for Django REST Framework discovery
from .auth import (
    SignupSerializer,
    SignupResponseSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    ErrorResponseSerializer
)
from .user import (
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    PublicUserSerializer
)
from .project import (
    ProjectSerializer,
    ProjectDetailSerializer,
    ProjectUpdateSerializer,
    ProjectStatsSerializer,
    ProjectConsentSerializer
)
from .resume import (
    ResumeTemplateSerializer,
    ResumeSerializer,
    ResumeGenerateRequestSerializer
)
from .upload import UploadFolderSerializer
from .portfolio import (
    PortfolioProjectSerializer,
    PortfolioSerializer,
    PortfolioGenerateSerializer,
    PortfolioEditSerializer,
    AddProjectSerializer,
    ReorderProjectsSerializer
)
from .evaluation import (
    ProjectEvaluationSerializer,
    ProjectEvaluationDetailSerializer,
    LanguageEvaluationStatsSerializer,
    EvaluationSummarySerializer,
    ProjectEvaluationListSerializer,
    LanguageComparisonSerializer,
)
