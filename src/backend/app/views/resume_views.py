from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from app.services.resume_service import list_templates, get_template, build_resume_context


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
