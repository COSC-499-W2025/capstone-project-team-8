from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from app.serializers import (
    ResumeTemplateSerializer,
    ResumeSerializer,
    ResumeGenerateRequestSerializer,
    ErrorResponseSerializer,
)

from app.models import Resume
from app.services.resume_service import list_templates, get_template, build_resume_context
from app.services.resume_builder.latex_generator import JakesResumeGenerator
from app.services.resume_builder.rendercv_generator import generate_pdf as rendercv_generate_pdf, generate_yaml_string


def _serialize_resume(resume):
    return {
        "id": resume.id,
        "name": resume.name,
        "content": resume.content,
        "theme": resume.theme,
        "rendercv_yaml": resume.rendercv_yaml,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
    }


def _build_resume_payload(request, resume=None):
    if "content" in request.data:
        content = request.data.get("content") or {}
    elif resume is not None:
        content = resume.content or {}
    else:
        content = {}

    if "theme" in request.data:
        theme = request.data.get("theme") or "classic"
    elif resume is not None and resume.theme:
        theme = resume.theme
    else:
        theme = "classic"

    if "name" in request.data:
        name = (request.data.get("name") or "").strip()
    elif resume is not None:
        name = resume.name
    else:
        name = ""

    if not isinstance(content, dict):
        raise ValueError("content must be an object")

    rendercv_yaml = generate_yaml_string(content, theme)
    return {
        "name": name,
        "content": content,
        "theme": theme,
        "rendercv_yaml": rendercv_yaml,
    }


@method_decorator(csrf_exempt, name="dispatch")
class ResumeListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ResumeSerializer(many=True)},
        description="List all saved resumes for the authenticated user",
        tags=["Resume"],
    )
    def get(self, request):
        resumes = Resume.objects.filter(user=request.user).order_by("-updated_at")
        return Response([_serialize_resume(resume) for resume in resumes])


@method_decorator(csrf_exempt, name="dispatch")
class ResumeTemplatesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ResumeTemplateSerializer(many=True)},
        description="List all available resume templates",
        tags=["Resume"],
    )
    def get(self, request):
        templates = list_templates()
        return Response({"templates": templates})


@method_decorator(csrf_exempt, name="dispatch")
class ResumePreviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='template_id', description='Template ID to preview', required=False, type=str),
        ],
        responses={200: OpenApiResponse(description="Resume preview with template and context")},
        description="Preview a resume template with user's context data",
        tags=["Resume"],
    )
    def get(self, request):
        template_id = request.query_params.get("template_id")
        template = get_template(template_id)
        context = build_resume_context(request.user)
        return Response({
            "template": template.as_dict(),
            "context": context,
        })


@method_decorator(csrf_exempt, name="dispatch")
class GenerateLatexResumeView(APIView):
    """
    API endpoint to generate a LaTeX resume using Jake's Resume template.
    Returns the LaTeX source code as a downloadable .tex file.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="LaTeX resume file (.tex)"),
            500: ErrorResponseSerializer,
        },
        description="Generate and download a LaTeX resume (.tex file) using Jake's Resume template",
        tags=["Resume"],
    )
    def get(self, request):
        """
        Generate and return a LaTeX resume for the authenticated user.
        
        Returns:
            - 200: LaTeX file with resume content
            - 500: Error during generation
        """
        try:
            # Generate the LaTeX resume
            generator = JakesResumeGenerator(request.user)
            latex_content = generator.generate()
            
            # Return as downloadable .tex file
            username = request.user.username
            filename = f"{username}_resume.tex"
            
            response = HttpResponse(latex_content, content_type='application/x-latex')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Failed to generate resume: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name="dispatch")
class ResumeDetailView(APIView):
    """
    GET /api/resume/{id}/
    Retrieve a specific resume by ID (only if owned by the authenticated user).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: ResumeSerializer,
            404: ErrorResponseSerializer,
        },
        description="Get a specific resume by ID",
        tags=["Resume"],
    )
    def get(self, request, pk):
        """Get a resume by ID."""
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        return Response(_serialize_resume(resume))


@method_decorator(csrf_exempt, name="dispatch")
class ResumeGenerateView(APIView):
    """
    POST /api/resume/generate/
    Generate a new resume for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ResumeGenerateRequestSerializer,
        responses={
            201: ResumeSerializer,
            400: ErrorResponseSerializer,
        },
        description="Generate a new resume",
        tags=["Resume"],
    )
    def post(self, request):
        """Generate a new resume."""
        name = (request.data.get("name") or "").strip()
        content = request.data.get("content") or {}
        if not name and not content:
            return Response(
                {"error": "name or content is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payload = _build_resume_payload(request)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not payload["name"]:
            payload["name"] = payload["content"].get("name") or f"Resume {request.user.resumes.count() + 1}"

        resume = Resume.objects.create(user=request.user, **payload)
        return Response(
            _serialize_resume(resume),
            status=status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name="dispatch")
class ResumeEditView(APIView):
    """
    POST /api/resume/{id}/edit/
    Edit an existing resume (only if owned by the authenticated user).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ResumeSerializer,
        responses={
            200: ResumeSerializer,
            404: ErrorResponseSerializer,
        },
        description="Edit an existing resume",
        tags=["Resume"],
    )
    def post(self, request, pk):
        """Edit an existing resume."""
        resume = get_object_or_404(Resume, pk=pk, user=request.user)

        try:
            payload = _build_resume_payload(request, resume=resume)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        resume.name = payload["name"]
        resume.content = payload["content"]
        resume.theme = payload["theme"]
        resume.rendercv_yaml = payload["rendercv_yaml"]
        resume.save()

        return Response(_serialize_resume(resume))


@method_decorator(csrf_exempt, name="dispatch")
class RenderCVPDFView(APIView):
    """
    POST /api/resume/render-pdf/

    Body:
        {
          "resumeData": { ...frontend resumeData object... },
          "theme": "classic" | "moderncv" | "engineeringclassic" | "sb2nov"
        }

    Returns:
        application/pdf  — the rendered PDF
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        resume_data = request.data.get("resumeData", {})
        theme = request.data.get("theme", "classic")

        if not resume_data:
            return Response(
                {"error": "resumeData is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pdf_bytes = rendercv_generate_pdf(resume_data, theme)
        except RuntimeError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="resume.pdf"'
        return response


@method_decorator(csrf_exempt, name="dispatch")
class RenderCVYAMLView(APIView):
    """
    POST /api/resume/render-yaml/

    Returns the RenderCV YAML string (useful for debugging / download).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        resume_data = request.data.get("resumeData", {})
        theme = request.data.get("theme", "classic")

        if not resume_data:
            return Response(
                {"error": "resumeData is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        yaml_str = generate_yaml_string(resume_data, theme)
        response = HttpResponse(yaml_str, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="resume.yaml"'
        return response
