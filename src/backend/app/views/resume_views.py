from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from app.models import Resume
from app.services.resume_service import list_templates, get_template, build_resume_context
from app.services.resume_builder.latex_generator import JakesResumeGenerator


@method_decorator(csrf_exempt, name="dispatch")
class ResumeTemplatesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = list_templates()
        return Response({"templates": templates})


@method_decorator(csrf_exempt, name="dispatch")
class ResumePreviewView(APIView):
    permission_classes = [IsAuthenticated]

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

    def get(self, request, pk):
        """Get a resume by ID."""
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        return Response({
            "id": resume.id,
            "name": resume.name,
            "content": resume.content,
            "created_at": resume.created_at,
            "updated_at": resume.updated_at,
        })


@method_decorator(csrf_exempt, name="dispatch")
class ResumeGenerateView(APIView):
    """
    POST /api/resume/generate/
    Generate a new resume for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Generate a new resume."""
        name = request.data.get("name")
        if not name:
            return Response(
                {"error": "name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        content = request.data.get("content", {})
        resume = Resume.objects.create(
            user=request.user,
            name=name,
            content=content
        )
        return Response(
            {
                "id": resume.id,
                "name": resume.name,
                "content": resume.content,
                "created_at": resume.created_at,
                "updated_at": resume.updated_at,
            },
            status=status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name="dispatch")
class ResumeEditView(APIView):
    """
    POST /api/resume/{id}/edit/
    Edit an existing resume (only if owned by the authenticated user).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Edit an existing resume."""
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        
        if "name" in request.data:
            resume.name = request.data["name"]
        if "content" in request.data:
            resume.content = request.data["content"]
        
        resume.save()
        
        return Response({
            "id": resume.id,
            "name": resume.name,
            "content": resume.content,
            "created_at": resume.created_at,
            "updated_at": resume.updated_at,
        })
