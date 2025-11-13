import io
import zipfile
from types import SimpleNamespace
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

def make_zip(files: dict) -> bytes:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for name, content in files.items():
            data = content.encode() if isinstance(content, str) else content
            z.writestr(name, data)
    return b.getvalue()

class UploadGithubFilterTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _upload(self, files, username=None):
        data = make_zip(files)
        upload = SimpleUploadedFile("u.zip", data, content_type="application/zip")
        form = {
            "file": upload,
            "consent_scan": "1",
        }
        if username:
            form["github_username"] = username
        return self.client.post("/api/upload-folder/", form)

    def test_filter_existing_user(self):
        # Fake analyzers (minimal)
        def fake_discover_projects(p):
            # Return a dict mapping the repo path to project tag 1
            repo_path = p / "repo"
            if repo_path.exists():
                return {repo_path: 1}
            return {}

        analyzers = SimpleNamespace(
            discover_projects=fake_discover_projects,
            analyze_image=lambda p: {"type": "image", "path": str(p), "size": 0},
            analyze_content=lambda p: {"type": "content", "path": str(p), "length": 1},
            analyze_code=lambda p: {"type": "code", "path": str(p), "lines": 1},
        )

        # Fake classifier
        classifier = SimpleNamespace(
            classify_project=lambda p: {"classification": "code", "confidence": 0.9}
        )

        # Fake git contributions (two contributors)
        def fake_git_contributors(_root):
            return {
                "contributors": {
                    "Jordan Truong": {
                        "commits": 5,
                        "lines_added": 120,
                        "lines_deleted": 10,
                        "email": "jordan@example.com",
                        "percent_of_commits": 62.5,
                    },
                    "Alice Smith": {
                        "commits": 3,
                        "lines_added": 40,
                        "lines_deleted": 5,
                        "email": "alice@example.com",
                        "percent_of_commits": 37.5,
                    },
                },
                "total_commits": 8,
            }

        def import_side(name):
            if name == "app.services.analyzers":
                return analyzers
            if name == "app.services.classifiers.project_classifier":
                return classifier
            if name == "app.services.gitFinder":
                return SimpleNamespace(get_git_contributors=fake_git_contributors)
            return SimpleNamespace()

        with patch("importlib.import_module", side_effect=import_side):
            resp = self._upload({"repo/.git/HEAD": "ref: heads/main", "repo/file.py": "print(1)"}, username="Jordan")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("user_contributions", data)
        uc = data["user_contributions"]
        self.assertTrue(uc["found"])
        self.assertEqual(uc["username"], "Jordan")
        # Projects must have only Jordan in contributors
        for project in data["projects"]:
            for c in project["contributors"]:
                self.assertIn("Jordan", c["name"])

    def test_filter_missing_user(self):
        def fake_discover_projects(p):
            # Return a dict mapping the repo path to project tag 1
            repo_path = p / "r"
            if repo_path.exists():
                return {repo_path: 1}
            return {}

        analyzers = SimpleNamespace(
            discover_projects=fake_discover_projects,
            analyze_image=lambda p: {"type": "image", "path": str(p), "size": 0},
            analyze_content=lambda p: {"type": "content", "path": str(p), "length": 1},
            analyze_code=lambda p: {"type": "code", "path": str(p), "lines": 1},
        )
        classifier = SimpleNamespace(
            classify_project=lambda p: {"classification": "code", "confidence": 0.9}
        )

        def fake_git_contributors(_root):
            return {
                "contributors": {
                    "Alice Smith": {
                        "commits": 2,
                        "lines_added": 30,
                        "lines_deleted": 4,
                        "email": "alice@example.com",
                        "percent_of_commits": 100.0,
                    }
                },
                "total_commits": 2,
            }

        def import_side(name):
            if name == "app.services.analyzers":
                return analyzers
            if name == "app.services.classifiers.project_classifier":
                return classifier
            if name == "app.services.gitFinder":
                return SimpleNamespace(get_git_contributors=fake_git_contributors)
            return SimpleNamespace()

        with patch("importlib.import_module", side_effect=import_side):
            resp = self._upload({"r/.git/HEAD": "ref: heads/main", "r/x.py": "print(1)"}, username="Jordan")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("user_contributions", data)
        self.assertFalse(data["user_contributions"]["found"])
        # Contributors lists should be empty after filtering
        for project in data["projects"]:
            self.assertEqual(len(project["contributors"]), 0)