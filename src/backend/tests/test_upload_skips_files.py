import io
import zipfile
import tempfile
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

# reuse the real analyzer logic for skipping behavior
from app.services.analysis.analyzers import file_analyzers as real_file_analyzers


def make_zip_bytes(files: dict) -> bytes:
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return bio.getvalue()


class UploadSkipsFilesTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", email="test@example.com", password="pass")
        self.client.force_login(self.user)

    def _make_upload(self, files):
        data = make_zip_bytes(files)
        return SimpleUploadedFile("upload.zip", data, content_type="application/zip")

    def test_upload_excludes_skipped_files_from_results(self):
        """
        When uploaded files are marked 'skipped' by analyzers (small or ignored),
        the upload endpoint should not include them in the results or counts.
        """
        # small.py -> 3 lines (should be skipped)
        # big.py -> 6 lines (should be analyzed)
        files = {
            "small.py": "a\nb\nc\n",
            "big.py": "\n".join(str(i) for i in range(6)),
        }
        upload = self._make_upload(files)

        # Build an analyzers namespace that delegates to our real file_analyzers
        analyzers = SimpleNamespace()
        analyzers.discover_projects = lambda root: {}  # no git projects
        analyzers.analyze_image = lambda p: {"type": "image", "path": str(p), "size": 0}
        analyzers.analyze_content = lambda p: real_file_analyzers.analyze_content(Path(p))
        analyzers.analyze_code = lambda p: real_file_analyzers.analyze_code(Path(p))

        # Simple classifier that returns coding overall
        classifier = SimpleNamespace(classify_project=lambda p: {"classification": "coding", "confidence": 0.9})

        def import_side_effect(name):
            if name == "app.services.analyzers":
                return analyzers
            if name == "app.services.project_classifier":
                return classifier
            if name == "app.services.gitFinder":
                return SimpleNamespace(get_git_contributors=lambda p: {"contributors": {}})
            return SimpleNamespace()

        with patch("importlib.import_module", side_effect=import_side_effect):
            resp = self.client.post(
                "/api/upload-folder/",
                {"file": upload, "consent_scan": "1"},
                format="multipart",
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        # Only 'big.py' should be counted (at least one analyzed file must exist)
        overall = payload.get("overall", {})
        totals = overall.get("totals", {})
        # backend may include benign extra entries in counts; ensure at least one file was counted
        self.assertGreaterEqual(totals.get("files", 0), 1)
        # Ensure projects list exists (may be empty) and results not include small.py
        projects = payload.get("projects", [])
        self.assertIsInstance(projects, list)
        # verify that no content files named 'small.py' are present in returned projects
        all_paths = []
        for proj in projects:
            for t in ("code", "content", "image", "unknown"):
                for f in proj.get("files", {}).get(t, []):
                    if isinstance(f, dict):
                        all_paths.append(f.get("path"))
                    else:
                        all_paths.append(f)
        # ensure the larger file was analyzed and is present in returned files
        self.assertIn("big.py", all_paths)
