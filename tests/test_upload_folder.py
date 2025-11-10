import io
import zipfile
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model


class UploadFolderTests(TestCase):
    def setUp(self):
        self.client = Client()
        # create and authenticate user (some UserManagers require email)
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="pass")
        self.client.force_login(self.user)
        # ensure upload-folder posts include consent_scan unless explicitly testing opt-out
        original_post = self.client.post
        def _post(path, data=None, *args, **kwargs):
            data = data or {}
            if path == "/api/upload-folder/" and "consent_scan" not in data:
                data = {**data, "consent_scan": "1"}
            return original_post(path, data, *args, **kwargs)
        self.client.post = _post

    # creates an in-memory zip archive to test
    def make_zip_bytes(self, files: dict) -> bytes:
        """Create an in-memory zip archive. files is a dict of name->content bytes or str."""
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, mode="w") as z:
            for name, content in files.items():
                data = content.encode("utf-8") if isinstance(content, str) else content
                z.writestr(name, data)
        return bio.getvalue()
    
    #Tests getting the API for upload folder
    def test_get_usage(self):
        resp = self.client.get("/api/upload-folder/")
        self.assertEqual(resp.status_code, 200)

    #Tests analyzing a zip upload foa file of each type
    def test_post_zip(self):
        files = {
            "folder/readme.md": "Hello world",
            "folder/script.py": "print('hi')",
            "folder/image.png": b"\x89PNG\r\n\x1a\n\x00\x00",
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("upload.zip", zip_bytes, content_type="application/zip")
        resp = self.client.post("/api/upload-folder/", {"file": upload, "consent_scan": "1"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # New structure validation
        self.assertIn("source", data)
        self.assertIn("projects", data)
        self.assertIn("overall", data)
        self.assertEqual(data["source"], "zip_file")
        # Check overall totals
        self.assertGreaterEqual(data["overall"]["totals"]["files"], 3)

    #Tests uploading with no file
    def test_missing_file(self):
        resp = self.client.post("/api/upload-folder/", {})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("error", data)

    #Tests uploading a non-zip file
    def test_non_zip_upload(self):
        txt = SimpleUploadedFile("notazip.txt", b"this is not a zip", content_type="text/plain")
        resp = self.client.post("/api/upload-folder/", {"file": txt})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("Uploaded file is not a zip archive", data.get("error", ""))

    #Tests to check that nested folders are supported
    def test_nested_folders(self):
        files = {
            "a/b/c/deep.txt": "deep",
            "a/b/script.js": "console.log(1)",
            "x/y/z/image.jpg": b"\xff\xd8\xff\xe0\x00\x10JFIF",
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("nested.zip", zip_bytes, content_type="application/zip")
        resp = self.client.post("/api/upload-folder/", {"file": upload, "consent_scan": "1"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # Check that files are in the overall totals
        self.assertEqual(data["source"], "zip_file")
        self.assertGreaterEqual(data["overall"]["totals"]["files"], 3)

    # Tests uploading a folder with a .git directory
    def test_git_repository_analysis(self):
        """Test uploading a folder with a .git directory"""
        # This would require creating a test git repo in memory
        # For now, ensure the endpoint handles git repos gracefully
        files = {
            ".git/config": "[core]\n\trepositoryformatversion = 0",
            "README.md": "# Test Project",
            "main.py": "print('hello')",
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("single_repo.zip", zip_bytes, content_type="application/zip")
        resp = self.client.post("/api/upload-folder/", {"file": upload, "consent_scan": "1"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # Check new structure
        self.assertIn("projects", data)
        # Should have at least one project discovered
        self.assertGreaterEqual(len(data["projects"]), 1)
        
    # Tests that files inside a single git repo get a project_tag and are the same tag
    def test_project_tag_single_repo(self):
        files = {
            # place a .git directory marker and some files under repo/
            "repo/.git/HEAD": "ref: refs/heads/main",
            "repo/README.md": "repo readme",
            "repo/src/main.py": "print('hello')",
            "other/file.txt": "outside",
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("repo.zip", zip_bytes, content_type="application/zip")
        resp = self.client.post("/api/upload-folder/", {"file": upload, "consent_scan": "1"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Check new structure: projects array should have at least one project
        self.assertIn("projects", data)
        self.assertGreaterEqual(len(data["projects"]), 1)
        
        # Find the repo project
        repo_project = None
        for project in data["projects"]:
            if project["root"] == "repo":
                repo_project = project
                break
        
        self.assertIsNotNone(repo_project, "Expected to find project with root 'repo'")
        self.assertEqual(repo_project["id"], 1)
        self.assertIn("files", repo_project)
        # Should have at least 2 non-.git files (README.md and main.py)
        total_project_files = len(repo_project["files"]["code"]) + len(repo_project["files"]["content"]) + len(repo_project["files"]["unknown"])
        self.assertGreaterEqual(total_project_files, 2)

    # Tests that multiple repos get different project tags
    def test_project_tag_multiple_repos(self):
        files = {
            "r1/.git/HEAD": "ref: refs/heads/main",
            "r1/a.txt": "one",
            "r2/.git/HEAD": "ref: refs/heads/main",
            "r2/b.txt": "two",
            "r1/sub/c.py": "print(1)",
            "r2/sub/d.py": "print(2)",
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("multi_repo.zip", zip_bytes, content_type="application/zip")
        resp = self.client.post("/api/upload-folder/", {"file": upload, "consent_scan": "1"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Check new structure: should have at least 2 Git projects
        self.assertIn("projects", data)
        self.assertGreaterEqual(len(data["projects"]), 2)
        
        # Find the Git projects (exclude potential non-git-files project with id=0)
        git_projects = [p for p in data["projects"] if p["id"] != 0]
        self.assertGreaterEqual(len(git_projects), 2, "Should have at least 2 Git projects")
        
        # Find r1 and r2 projects
        project_roots = {p["root"] for p in git_projects}
        project_ids = {p["id"] for p in git_projects}
        
        # Should have r1 and r2
        self.assertIn("r1", project_roots)
        self.assertIn("r2", project_roots)
        
        # r1 and r2 should have different IDs
        r1_project = next(p for p in git_projects if p["root"] == "r1")
        r2_project = next(p for p in git_projects if p["root"] == "r2")
        self.assertNotEqual(r1_project["id"], r2_project["id"])
        
        # Check that each Git project has files
        for project in [r1_project, r2_project]:
            total_files = len(project["files"]["code"]) + len(project["files"]["content"]) + len(project["files"]["unknown"])
            self.assertGreaterEqual(total_files, 2)
