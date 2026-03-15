from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count, Prefetch
from datetime import datetime
import math
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from app.serializers import (
    ProjectSerializer,
    ProjectDetailSerializer,
    ProjectUpdateSerializer,
    ProjectStatsSerializer,
    ProjectConsentSerializer,
    ErrorResponseSerializer,
)
from app.services.llm import ai_analyze
from app.utils.prompt_loader import load_prompt_template
import logging

logger = logging.getLogger(__name__)

from app.models import (
    Project, ProjectFile, Contributor, ProjectContribution,
    ProjectLanguage, ProjectFramework, ProgrammingLanguage, Framework, ProjectEvaluation,
)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectsListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='q', description='Search projects by name', required=False, type=str),
        ],
        responses={200: ProjectSerializer(many=True)},
        description="List all projects for the authenticated user. Optionally filter by name using the 'q' query parameter.",
        tags=["Projects"],
    )
    def get(self, request):
        """
        List projects for the authenticated user.
        Supports optional ?q= search by project name.
        """
        q = request.GET.get("q", "").strip()
        
        # Optimize queries with select_related and prefetch_related
        qs = Project.objects.filter(
            user=request.user
        ).select_related(
            'user'
        ).prefetch_related(
            'languages',
            'frameworks'
        ).order_by("-created_at")
        
        if q:
            qs = qs.filter(name__icontains=q)

        out = []
        for p in qs:
            # Get framework count without additional query (prefetched)
            framework_count = p.frameworks.all().count()
            
            # Extract languages and frameworks for resume builder
            languages = [{"id": l.id, "name": l.name} for l in p.languages.all()]
            frameworks = [{"id": f.id, "name": f.name} for f in p.frameworks.all()]
            
            out.append({
                "id": p.id,
                "name": p.name,
                "project_tag": p.project_tag,
                "project_root_path": p.project_root_path,
                "classification_type": p.classification_type,
                "classification_confidence": float(p.classification_confidence or 0.0),
                "total_files": int(p.total_files or 0),
                "code_files_count": int(p.code_files_count or 0),
                "text_files_count": int(p.text_files_count or 0),
                "image_files_count": int(p.image_files_count or 0),
                "git_repository": bool(p.git_repository),
                "first_commit_date": int(p.first_commit_date.timestamp()) if p.first_commit_date else None,
                "created_at": int(p.created_at.timestamp()) if p.created_at else None,
                "updated_at": int(p.updated_at.timestamp()) if p.updated_at else None,
                "thumbnail_url": request.build_absolute_uri(p.thumbnail.url) if p.thumbnail else None,
                "framework_count": framework_count,
                "languages": languages,
                "frameworks": frameworks,
                "resume_bullet_points": p.resume_bullet_points or [],
                "user_role": p.user_role or 'other',
            })

        return JsonResponse({"projects": out})


@method_decorator(csrf_exempt, name="dispatch")
class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_project(self, pk, user):
        try:
            return Project.objects.get(pk=pk, user=user)
        except Project.DoesNotExist:
            return None

    @extend_schema(
        responses={
            200: ProjectDetailSerializer,
            404: ErrorResponseSerializer,
        },
        description="Get detailed information about a specific project",
        tags=["Projects"],
    )
    def get(self, request, pk):
        p = self._get_project(pk, request.user)
        if not p:
            return JsonResponse({"error": "Project not found"}, status=404)

        # Files
        files_qs = ProjectFile.objects.filter(project=p)
        files = {"code": [], "content": [], "image": [], "unknown": []}
        for f in files_qs:
            entry = {
                "filename": f.filename,
                "file_path": f.file_path,
                "file_extension": f.file_extension,
                "file_type": f.file_type,
                "file_size_bytes": f.file_size_bytes,
                "line_count": f.line_count,
                "character_count": f.character_count,
                "content_preview": (f.content_preview or "")[:200]
            }
            files.setdefault(f.file_type or "unknown", []).append(entry)

        # Contributors
        contribs_qs = ProjectContribution.objects.filter(project=p).select_related("contributor")
        contributors = []
        for c in contribs_qs:
            contributors.append({
                "name": c.contributor.name,
                "email": c.contributor.email,
                "commits": c.commit_count,
                "lines_added": c.lines_added,
                "lines_deleted": c.lines_deleted,
                "percent_of_commits": float(c.percent_of_commits or 0.0)
            })

        # Compute highlight score (same formula as _get_ranked_projects)
        user_contribution = ProjectContribution.objects.filter(
            project=p, contributor__user=request.user
        ).first()
        total_project_lines = ProjectFile.objects.filter(
            project=p, file_type='code'
        ).aggregate(total=Sum('line_count'))['total'] or 0

        total_lines_changed = 0
        if user_contribution:
            total_lines_changed = user_contribution.lines_added + user_contribution.lines_deleted

        eval_obj = ProjectEvaluation.objects.filter(project=p).first()
        quality_score = eval_obj.overall_score if eval_obj else 0.0

        if total_project_lines > 0:
            scale_score = min((math.log2(total_project_lines) / 13.3) * 100, 100)
        else:
            scale_score = 0.0

        if total_lines_changed > 0:
            effort_score = min((math.log2(total_lines_changed) / 13.3) * 100, 100)
        else:
            effort_score = 0.0

        langs = list(
            ProjectLanguage.objects.filter(project=p)
            .select_related('language')
            .values_list('language__name', flat=True)[:5]
        )
        fws = list(
            ProjectFramework.objects.filter(project=p)
            .select_related('framework')
            .values_list('framework__name', flat=True)[:5]
        )
        breadth_score = min(((len(langs) + len(fws)) / 10) * 100, 100)

        highlight_score = (
            quality_score * 0.40 +
            scale_score * 0.25 +
            effort_score * 0.20 +
            breadth_score * 0.15
        )

        resp = {
            "id": p.id,
            "name": p.name,
            "project_tag": p.project_tag,
            "project_root_path": p.project_root_path,
            "classification_type": p.classification_type,
            "classification_confidence": float(p.classification_confidence or 0.0),
            "total_files": int(p.total_files or 0),
            "files": files,
            "contributors": contributors,
            "git_repository": bool(p.git_repository),
            "first_commit_date": int(p.first_commit_date.timestamp()) if p.first_commit_date else None,
            "created_at": int(p.created_at.timestamp()) if p.created_at else None,
            "resume_bullet_points": p.resume_bullet_points or [],
            "user_role": p.user_role or 'other',
            "highlight_score": round(highlight_score, 1),
            "score_breakdown": {
                "quality": round(quality_score, 1),
                "scale": round(scale_score, 1),
                "effort": round(effort_score, 1),
                "breadth": round(breadth_score, 1),
            },
        }
        return JsonResponse(resp)

    @extend_schema(
        request=ProjectUpdateSerializer,
        responses={
            200: OpenApiResponse(description="Project updated successfully"),
            404: ErrorResponseSerializer,
        },
        description="Update project name and/or description",
        tags=["Projects"],
    )
    def patch(self, request, pk):
        p = self._get_project(pk, request.user)
        if not p:
            return JsonResponse({"error": "Project not found"}, status=404)

        # Expect JSON body; only allow name and description updates
        try:
            data = request.data if hasattr(request, "data") else {}
        except Exception:
            data = {}

        from app.serializers.project import VALID_USER_ROLES
        from django.utils import timezone

        name = data.get("name")
        description = data.get("description")
        user_role = data.get("user_role")
        changed = False

        if user_role is not None:
            if user_role not in VALID_USER_ROLES:
                return JsonResponse(
                    {"error": f"Invalid user_role '{user_role}'. Valid choices: {VALID_USER_ROLES}"},
                    status=400,
                )
            p.user_role = user_role
            changed = True

        if name:
            p.name = str(name)[:255]
            changed = True
        if description is not None:
            # If Project model has a description field, set it; otherwise ignore
            if hasattr(p, "description"):
                p.description = str(description)[:2000]
                changed = True

        if changed:
            p.updated_at = timezone.now()
            p.save()

        return JsonResponse({"ok": True, "id": p.id})

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Project deleted successfully"),
            404: ErrorResponseSerializer,
        },
        description="Delete a project",
        tags=["Projects"],
    )
    def delete(self, request, pk):
        p = self._get_project(pk, request.user)
        if not p:
            return JsonResponse({"error": "Project not found"}, status=404)
        p.delete()
        return JsonResponse({"ok": True, "deleted_id": pk})


@method_decorator(csrf_exempt, name="dispatch")
class ProjectStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ProjectStatsSerializer},
        description="Get overall project statistics for the authenticated user including totals, languages, and frameworks",
        tags=["Projects"],
    )
    def get(self, request):
        """
        Return overall project statistics for the authenticated user.
        """
        user_projects = Project.objects.filter(user=request.user)
        total_projects = user_projects.count()

        totals = user_projects.aggregate(
            total_files=Sum("total_files"),
            code_files=Sum("code_files_count"),
            text_files=Sum("text_files_count"),
            image_files=Sum("image_files_count")
        )

        # Top languages across user's projects (based on ProjectLanguage.file_count)
        lang_stats = []
        lang_qs = ProjectLanguage.objects.filter(project__user=request.user).values("language__name").annotate(total=Sum("file_count")).order_by("-total")
        for l in lang_qs:
            lang_stats.append({"language": l["language__name"], "file_count": int(l["total"] or 0)})

        # Top frameworks across user's projects
        framework_stats = []
        fw_qs = ProjectFramework.objects.filter(project__user=request.user).values("framework__name").annotate(count=Count("id")).order_by("-count")
        for f in fw_qs:
            framework_stats.append({"framework": f["framework__name"], "projects_count": int(f["count"] or 0)})

        resp = {
            "total_projects": total_projects,
            "total_files": int(totals.get("total_files") or 0),
            "code_files": int(totals.get("code_files") or 0),
            "text_files": int(totals.get("text_files") or 0),
            "image_files": int(totals.get("image_files") or 0),
            "top_languages": lang_stats,
            "top_frameworks": framework_stats
        }
        return JsonResponse(resp)


def _get_ranked_projects(user):
    """
    Get projects ranked by a composite highlight score that balances
    quality, scale, effort, and breadth — so team projects aren't
    automatically beaten by trivial solo projects.

    Composite highlight_score (0–100):
      Quality  (40%) — evaluation overall_score (0-100)
      Scale    (25%) — log-scaled total lines of code
      Effort   (20%) — log-scaled absolute lines the user changed
      Breadth  (15%) — number of distinct languages + frameworks (capped at 10)
    """
    projects = Project.objects.filter(user=user).prefetch_related(
        'files', 'contributions', 'languages', 'frameworks'
    )

    project_rows = []

    for project in projects:
        user_contributions = ProjectContribution.objects.filter(
            project=project,
            contributor__user=user
        ).first()

        total_project_lines = ProjectFile.objects.filter(
            project=project,
            file_type='code'
        ).aggregate(total=Sum('line_count'))['total'] or 0

        commit_percentage = 0.0
        total_lines_changed = 0
        commit_count = 0

        if user_contributions:
            commit_percentage = user_contributions.percent_of_commits or 0.0
            total_lines_changed = user_contributions.lines_added + user_contributions.lines_deleted
            commit_count = user_contributions.commit_count

        # Get languages (top 5)
        languages = list(
            ProjectLanguage.objects.filter(project=project)
            .select_related('language')
            .order_by('-file_count')
            .values_list('language__name', flat=True)[:5]
        )

        # Get frameworks (top 5)
        frameworks = list(
            ProjectFramework.objects.filter(project=project)
            .select_related('framework')
            .values_list('framework__name', flat=True)[:5]
        )

        # --- Compute sub-scores ---
        # Quality: evaluation overall_score (0-100), default 0
        eval_obj = ProjectEvaluation.objects.filter(project=project).first()
        quality_score = eval_obj.overall_score if eval_obj else 0.0

        # Scale: log-scaled total lines of code (log2 of lines, normalized 0-100)
        # log2(10000) ≈ 13.3 → treat 10k+ lines as ~100
        if total_project_lines > 0:
            scale_score = min((math.log2(total_project_lines) / 13.3) * 100, 100)
        else:
            scale_score = 0.0

        # Effort: log-scaled absolute lines changed by the user
        if total_lines_changed > 0:
            effort_score = min((math.log2(total_lines_changed) / 13.3) * 100, 100)
        else:
            effort_score = 0.0

        # Breadth: number of languages + frameworks (cap at 10 → 100)
        breadth_raw = len(languages) + len(frameworks)
        breadth_score = min((breadth_raw / 10) * 100, 100)

        # Weighted composite
        highlight_score = (
            quality_score  * 0.40 +
            scale_score    * 0.25 +
            effort_score   * 0.20 +
            breadth_score  * 0.15
        )

        if total_project_lines > 0:
            lines_changed_percentage = (total_lines_changed / total_project_lines) * 100
        else:
            lines_changed_percentage = 0.0

        project_rows.append({
            "id": project.id,
            "name": project.name,
            "project_tag": project.project_tag,
            "project_root_path": project.project_root_path,
            "classification_type": project.classification_type,
            "classification_confidence": float(project.classification_confidence or 0.0),
            "git_repository": bool(project.git_repository),
            "highlight_score": round(highlight_score, 1),
            "contribution_score": round(
                (commit_percentage * 0.4) + (lines_changed_percentage * 0.6), 2
            ),
            "commit_percentage": round(commit_percentage, 2),
            "lines_changed_percentage": round(lines_changed_percentage, 2),
            "total_commits": commit_count,
            "total_lines_changed": total_lines_changed,
            "total_project_lines": total_project_lines,
            "first_commit_date": int(project.first_commit_date.timestamp()) if project.first_commit_date else None,
            "languages": languages,
            "frameworks": frameworks,
            "resume_bullet_points": project.resume_bullet_points or [],
            "score_breakdown": {
                "quality": round(quality_score, 1),
                "scale": round(scale_score, 1),
                "effort": round(effort_score, 1),
                "breadth": round(breadth_score, 1),
            },
        })

    project_rows.sort(key=lambda x: x['highlight_score'], reverse=True)
    return project_rows


@method_decorator(csrf_exempt, name="dispatch")
class RankedProjectsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description="Projects ranked by highlight score")},
        description="Return projects ranked by composite highlight score (quality, scale, effort, breadth)",
        tags=["Projects"],
    )
    def get(self, request):
        """
        Return projects ranked by composite highlight score.

        Highlight Score Formula (0–100):
          Quality  (40%) — evaluation overall_score
          Scale    (25%) — log₂-scaled total lines of code
          Effort   (20%) — log₂-scaled absolute lines changed
          Breadth  (15%) — distinct languages + frameworks (capped at 10)
        """
        ranked_projects = _get_ranked_projects(request.user)
        return JsonResponse({"projects": ranked_projects})

@method_decorator(csrf_exempt, name="dispatch")
class TopProjectsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description="Top 3 ranked projects with AI summaries")},
        description="Return top 3 ranked projects with pre-generated AI summaries",
        tags=["Projects"],
    )
    def get(self, request):
        """Return top 3 ranked projects with pre-generated AI summaries."""
        projects = _get_ranked_projects(request.user)[:3]
        
        results = []
        for project_data in projects:
            # Fetch the actual Project model instance to access ai_summary and llm_consent
            project_obj = Project.objects.filter(id=project_data['id']).first()
            
            # Evaluation data for quality evolution
            evaluation = None
            if project_obj:
                eval_obj = ProjectEvaluation.objects.filter(project=project_obj).first()
                if eval_obj:
                    evaluation = {
                        "overall_score": round(eval_obj.overall_score, 1),
                        "code_quality_score": round(eval_obj.code_quality_score, 1),
                        "documentation_score": round(eval_obj.documentation_score, 1),
                        "structure_score": round(eval_obj.structure_score, 1),
                        "testing_score": round(eval_obj.testing_score, 1),
                    }
            
            # File composition breakdown
            file_composition = {"code": 0, "content": 0, "image": 0}
            if project_obj:
                file_composition = {
                    "code": int(project_obj.code_files_count or 0),
                    "content": int(project_obj.text_files_count or 0),
                    "image": int(project_obj.image_files_count or 0),
                }
            
            results.append({
                "project_id": project_data['id'],
                "name": project_data['name'],
                "project_tag": project_data['project_tag'],
                "project_root_path": project_data['project_root_path'],
                "classification_type": project_data['classification_type'],
                "classification_confidence": project_data['classification_confidence'],
                "git_repository": project_data['git_repository'],
                "highlight_score": project_data['highlight_score'],
                "score_breakdown": project_data['score_breakdown'],
                "contribution_score": project_data['contribution_score'],
                "commit_percentage": project_data['commit_percentage'],
                "lines_changed_percentage": project_data['lines_changed_percentage'],
                "total_commits": project_data['total_commits'],
                "total_lines_changed": project_data['total_lines_changed'],
                "total_project_lines": project_data['total_project_lines'],
                "total_files": file_composition['code'] + file_composition['content'] + file_composition['image'],
                "file_composition": file_composition,
                "first_commit_date": project_data['first_commit_date'],
                "created_at": int(project_obj.created_at.timestamp()) if project_obj and project_obj.created_at else None,
                "languages": project_data['languages'],
                "frameworks": project_data['frameworks'],
                "summary": project_obj.ai_summary if project_obj and project_obj.ai_summary else "No summary available",
                "llm_consent": project_obj.llm_consent if project_obj else False,
                "evaluation": evaluation,
            })
        
        return JsonResponse({"top_projects": results}, status=200)
    
    def _build_project_context(self, project_data: dict) -> str:
        """Build formatted context string for LLM."""
        date_info = ""
        if project_data.get('first_commit_date'):
            try:
                date = datetime.fromtimestamp(project_data['first_commit_date'])
                date_info = f"- First Commit Date: {date.strftime('%B %Y')}\n"
            except:
                pass
        
        languages = project_data.get('languages', [])
        languages_str = ", ".join(languages) if languages else "None detected"
        
        frameworks = project_data.get('frameworks', [])
        frameworks_str = ", ".join(frameworks) if frameworks else "None detected"
        
        context = f"""
Project Name: {project_data.get('name', 'Unknown')}
Classification: {project_data.get('classification_type', 'unknown')}
Primary Languages: {languages_str}
Frameworks: {frameworks_str}
Contribution Score: {project_data.get('contribution_score', 0)}/100
Commit Percentage: {project_data.get('commit_percentage', 0)}%
Lines Changed Percentage: {project_data.get('lines_changed_percentage', 0)}%
Total Commits: {project_data.get('total_commits', 0)}
{date_info}
"""
        return context.strip()
    
    def _generate_summary(self, context: str) -> str:
        """Generate summary using Azure OpenAI."""
        try:
            template = load_prompt_template('project_contribution_summary')
            full_prompt = template.build_prompt(context)
            
            system_msg = """You are a professional resume writer specializing in software engineering portfolios.

Generate concise, impactful 2-3 sentence summaries suitable for a portfolio or resume.

Guidelines:
- Focus on technical achievements and quantifiable contributions
- Highlight key technologies prominently
- Use active voice and emphasize impact
- If high contribution (>50%), emphasize leadership
- If moderate (20-50%), emphasize collaboration
- Keep it professional and compelling

Output ONLY the summary text."""
            
            summary = ai_analyze(full_prompt, system_message=system_msg)
            return summary if summary else "Unable to generate summary at this time."
            
        except FileNotFoundError as e:
            logger.error(f"Prompt template not found: {e}")
            return "Summary generation unavailable."
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Unable to generate summary at this time."


@method_decorator(csrf_exempt, name="dispatch")
class ProjectThumbnailUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={'multipart/form-data': {'type': 'object', 'properties': {'thumbnail': {'type': 'string', 'format': 'binary'}}}},
        responses={
            200: OpenApiResponse(description="Thumbnail uploaded successfully"),
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        description="Upload a thumbnail image for a project",
        tags=["Projects"],
    )
    def post(self, request, pk):
        """POST endpoint to upload project thumbnail image."""
        try:
            project = Project.objects.get(pk=pk, user=request.user)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=404)
        
        if 'thumbnail' not in request.FILES:
            return JsonResponse({'detail': 'No image file provided'}, status=400)
        
        image_file = request.FILES['thumbnail']
        
        # Validate file is an image
        if not image_file.content_type.startswith('image/'):
            return JsonResponse({'detail': 'File must be an image'}, status=400)
        
        # Optional: Check file size (e.g., max 5MB)
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({'detail': 'Image must be smaller than 5MB'}, status=400)
        
        # Delete old thumbnail if exists
        if project.thumbnail:
            project.thumbnail.delete()
        
        # Save new thumbnail
        project.thumbnail = image_file
        project.save()
        
        # Build absolute URL for the thumbnail
        thumbnail_url = project.thumbnail.url if project.thumbnail else None
        if thumbnail_url:
            thumbnail_url = request.build_absolute_uri(thumbnail_url)
        
        return JsonResponse({
            'detail': 'Project thumbnail uploaded successfully',
            'project': {
                'id': project.id,
                'name': project.name,
                'thumbnail_url': thumbnail_url,
            }
        })


@method_decorator(csrf_exempt, name="dispatch")
class LLMPrivacyConsentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProjectConsentSerializer,
        responses={
            200: OpenApiResponse(description="Consent updated successfully"),
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        description="Update LLM consent for a project",
        tags=["Projects"],
    )
    def post(self, request):
        serializer = ProjectConsentSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        project_id = serializer.validated_data['project_id']
        consent = serializer.validated_data['consent']

        try:
            project = Project.objects.get(pk=project_id, user=request.user)
            project.llm_consent = consent
            project.save()

            return JsonResponse({
                'id': project.id,
                'llm_consent': project.llm_consent,
                'message': 'Consent updated successfully'
            })
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=404)
