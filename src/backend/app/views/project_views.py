from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count

from app.models import (
    Project, ProjectFile, Contributor, ProjectContribution,
    ProjectLanguage, ProjectFramework, ProgrammingLanguage, Framework
)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        List projects for the authenticated user.
        Supports optional ?q= search by project name.
        """
        q = request.GET.get("q", "").strip()
        qs = Project.objects.filter(user=request.user).order_by("-id")
        if q:
            qs = qs.filter(name__icontains=q)

        out = []
        for p in qs:
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
                "created_at": int(p.created.timestamp()) if getattr(p, "created", None) else None
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
            "created_at": int(p.created.timestamp()) if getattr(p, "created", None) else None,
        }
        return JsonResponse(resp)

    def patch(self, request, pk):
        p = self._get_project(pk, request.user)
        if not p:
            return JsonResponse({"error": "Project not found"}, status=404)

        # Expect JSON body; only allow name and description updates
        try:
            data = request.data if hasattr(request, "data") else {}
        except Exception:
            data = {}

        name = data.get("name")
        description = data.get("description")
        changed = False
        if name:
            p.name = str(name)[:255]
            changed = True
        if description is not None:
            # If Project model has a description field, set it; otherwise ignore
            if hasattr(p, "description"):
                p.description = str(description)[:2000]
                changed = True

        if changed:
            p.save()

        return JsonResponse({"ok": True, "id": p.id})

    def delete(self, request, pk):
        p = self._get_project(pk, request.user)
        if not p:
            return JsonResponse({"error": "Project not found"}, status=404)
        p.delete()
        return JsonResponse({"ok": True, "deleted_id": pk})


@method_decorator(csrf_exempt, name="dispatch")
class ProjectStatsView(APIView):
    permission_classes = [IsAuthenticated]

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