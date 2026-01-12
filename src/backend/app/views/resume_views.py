from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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
