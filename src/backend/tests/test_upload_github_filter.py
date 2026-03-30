import io
import zipfile
from types import SimpleNamespace
from pathlib import Path
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

def make_zip(files: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, content in files.items():
            data = content.encode() if isinstance(content, str) else content
            z.writestr(name, data)
    return buf.getvalue()

class UploadGithubFilterTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _upload(self, files, username=None):
        data = make_zip(files)
        upload = SimpleUploadedFile("upload.zip", data, content_type="application/zip")
        form = {"file": upload, "consent_scan": "1"}
        if username:
            form["github_username"] = username
        return self.client.post("/api/upload-folder/", form)

    def _build_patches(self, discover_func, git_contrib_func, classifier_func=None, timestamp_func=None):
        # Analyzers mock (only need discover + file analyzers)
        analyzers = SimpleNamespace(
            discover_projects=discover_func,
            analyze_image=lambda p: {"type": "image", "path": str(p), "size": 0},
            analyze_content=lambda p: {"type": "content", "path": str(p), "length": 1},
            analyze_code=lambda p: {"type": "code", "path": str(p), "lines": 1},
        )
        # Classifier mock
        classifier = SimpleNamespace(
            classify_project=classifier_func or (lambda p: {"classification": "code", "confidence": 0.9})
        )
        # Git contributions mock
        git_module = SimpleNamespace(
            get_git_contributors=git_contrib_func,
            get_project_timestamp=timestamp_func or (lambda p: 1700000000),
        )
        # importlib side effect
        def import_side(name):
            if name == "app.services.classifiers.project_classifier":
                return classifier
            if name == "app.services.analysis.analyzers.git_contributions":
                return git_module
            raise ImportError(f"No module named '{name}'")
        return analyzers, import_side

    # ---------------- Tests ----------------

    def test_filter_existing_user(self):
        def discover(tmpdir):
            repo = tmpdir / "repo"
            return {repo: 1} if repo.exists() else {}
        def git_contrib(_):
            return {
                "contributors": {
                    "Jordan Truong": {
                        "commits": 5,
                        "lines_added": 120,
                        "lines_deleted": 10,
                        "email": "jordan@example.com",
                        "percent_of_commits": 62.5
                    },
                    "Alice Smith": {
                        "commits": 3,
                        "lines_added": 40,
                        "lines_deleted": 5,
                        "email": "alice@example.com",
                        "percent_of_commits": 37.5
                    },
                },
                "total_commits": 8
            }
        analyzers, import_side = self._build_patches(discover, git_contrib)
        with patch("app.services.analysis.analyzers", analyzers), \
             patch("app.services.folder_upload.folder_upload_service.importlib.import_module", side_effect=import_side):
            resp = self._upload(
                {"repo/.git/HEAD": "ref: heads/main", "repo/file.py": "print(1)"},
                username="Jordan"
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Username echo + user_contributions
        self.assertIn("username_entered", data)
        self.assertEqual(data["username_entered"], "Jordan")
        self.assertIn("user_contributions", data)
        uc = data["user_contributions"]
        self.assertTrue(uc["found"])
        self.assertEqual(uc["totals"]["commits"], 5)

        # Identify the real repo project (exclude id=0 unorganized)
        real_projects = [p for p in data["projects"] if p["id"] != 0]
        self.assertEqual(len(real_projects), 1, "Expected exactly one Git project")
        repo_project = real_projects[0]

        # Contributors list should be full (2 contributors)
        self.assertEqual(len(repo_project["contributors"]), 2)
        names = {c["name"] for c in repo_project["contributors"]}
        self.assertEqual(names, {"Jordan Truong", "Alice Smith"})

        # If unorganized project present, its contributors should be empty
        unorganized = [p for p in data["projects"] if p["id"] == 0]
        if unorganized:
            self.assertEqual(len(unorganized[0]["contributors"]), 0)

    def test_filter_missing_user(self):
        def discover(tmpdir):
            r = tmpdir / "r"
            return {r: 1} if r.exists() else {}
        def git_contrib(_):
            return {
                "contributors": {
                    "Alice Smith": {"commits": 2, "lines_added": 30, "lines_deleted": 4, "email": "alice@example.com", "percent_of_commits": 100.0}
                },
                "total_commits": 2,
            }
        analyzers, import_side = self._build_patches(discover, git_contrib)
        with patch("app.services.analysis.analyzers", analyzers), \
             patch("app.services.folder_upload.folder_upload_service.importlib.import_module", side_effect=import_side):
            resp = self._upload({"r/.git/HEAD": "ref: heads/main", "r/x.py": "print(1)"}, username="Jordan")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["username_entered"], "Jordan")
        uc = data["user_contributions"]
        self.assertFalse(uc["found"])
        self.assertEqual(len(uc["projects"]), 0)
        project = data["projects"][0]
        self.assertEqual(len(project["contributors"]), 1)
        self.assertEqual(project["contributors"][0]["name"], "Alice Smith")

    def test_no_username_provided(self):
        def discover(tmpdir):
            repo = tmpdir / "repo"
            return {repo: 1} if repo.exists() else {}
        def git_contrib(_):
            return {
                "contributors": {
                    "Jordan Truong": {"commits": 5, "lines_added": 120, "lines_deleted": 10, "email": "jordan@example.com", "percent_of_commits": 62.5},
                    "Alice Smith": {"commits": 3, "lines_added": 40, "lines_deleted": 5, "email": "alice@example.com", "percent_of_commits": 37.5},
                },
                "total_commits": 8,
            }
        analyzers, import_side = self._build_patches(discover, git_contrib)
        with patch("app.services.analysis.analyzers", analyzers), \
             patch("app.services.folder_upload.folder_upload_service.importlib.import_module", side_effect=import_side):
            resp = self._upload({"repo/.git/HEAD": "ref: heads/main", "repo/file.py": "print(1)"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertNotIn("username_entered", data)
        self.assertNotIn("user_contributions", data)
        contributors = data["projects"][0]["contributors"]
        self.assertEqual(len(contributors), 2)

    def test_filter_by_first_name_only(self):
        def discover(tmpdir):
            repo = tmpdir / "repo"
            return {repo: 1} if repo.exists() else {}
        def git_contrib(_):
            return {
                "contributors": {
                    "Jordan Truong": {"commits": 5, "lines_added": 120, "lines_deleted": 10, "email": "jordan@example.com", "percent_of_commits": 62.5},
                    "Alice Smith": {"commits": 3, "lines_added": 40, "lines_deleted": 5, "email": "alice@example.com", "percent_of_commits": 37.5},
                },
                "total_commits": 8,
            }
        analyzers, import_side = self._build_patches(discover, git_contrib)
        with patch("app.services.analysis.analyzers", analyzers), \
             patch("app.services.folder_upload.folder_upload_service.importlib.import_module", side_effect=import_side):
            resp = self._upload({"repo/.git/HEAD": "ref: heads/main", "repo/file.py": "print(1)"}, username="jordan")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["username_entered"], "jordan")
        uc = data["user_contributions"]
        self.assertTrue(uc["found"])
        self.assertEqual(uc["totals"]["commits"], 5)
        self.assertEqual(len(data["projects"][0]["contributors"]), 2)

    def test_filter_by_email_local_part(self):
        def discover(tmpdir):
            repo = tmpdir / "webapp"
            return {repo: 1} if repo.exists() else {}
        def git_contrib(_):
            return {
                "contributors": {
                    "J. Truong": {"commits": 7, "lines_added": 200, "lines_deleted": 15, "email": "jordan@example.com", "percent_of_commits": 100.0},
                },
                "total_commits": 7,
            }
        analyzers, import_side = self._build_patches(discover, git_contrib)
        with patch("app.services.analysis.analyzers", analyzers), \
             patch("app.services.folder_upload.folder_upload_service.importlib.import_module", side_effect=import_side):
            resp = self._upload({"webapp/.git/HEAD": "ref: heads/main", "webapp/index.js": "console.log('hi')"}, username="jordan")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        uc = data["user_contributions"]
        self.assertTrue(uc["found"])
        self.assertEqual(uc["totals"]["commits"], 7)
        self.assertEqual(data["projects"][0]["contributors"][0]["name"], "J. Truong")

    def test_case_insensitive_match(self):
        def discover(tmpdir):
            repo = tmpdir / "lib"
            return {repo: 1} if repo.exists() else {}
        def git_contrib(_):
            return {
                "contributors": {
                    "ALICE SMITH": {"commits": 10, "lines_added": 300, "lines_deleted": 20, "email": "alice@test.com", "percent_of_commits": 100.0},
                },
                "total_commits": 10,
            }
        analyzers, import_side = self._build_patches(discover, git_contrib)
        with patch("app.services.analysis.analyzers", analyzers), \
             patch("app.services.folder_upload.folder_upload_service.importlib.import_module", side_effect=import_side):
            resp = self._upload({"lib/.git/HEAD": "ref: heads/main", "lib/util.py": "pass"}, username="alice smith")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        uc = data["user_contributions"]
        self.assertTrue(uc["found"])
        self.assertEqual(uc["totals"]["commits"], 10)