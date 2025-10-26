import io
import zipfile
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile


class UploadFolderTests(TestCase):
    def setUp(self):
        self.client = Client()

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
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 3)
        types = {item.get("type") for item in data["results"]}
        self.assertIn("content", types)
        self.assertIn("code", types)

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
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        paths = {item.get("path") for item in data["results"]}
        self.assertTrue(any("deep.txt" in p for p in paths))
        self.assertTrue(any("script.js" in p for p in paths))
        self.assertTrue(any("image.jpg" in p for p in paths))

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
        upload = SimpleUploadedFile("git-repo.zip", zip_bytes, content_type="application/zip")
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # Check that git analysis was attempted
        self.assertIn("results", data)
        
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
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # collect project tags for files under repo/
        repo_tags = {
            item.get("project_tag")
            for item in data["results"]
            if item.get("path", "").startswith("repo/") and ".git/" not in item.get("path", "")
        }

        # files in repo should have a tag and all the same tag
        self.assertTrue(len(repo_tags) == 1, f"Expected one tag for repo files, got {repo_tags}")
        self.assertIsNotNone(next(iter(repo_tags)))
        
        git_tags = {
            item.get("project_tag")
            for item in data["results"]
            if item.get("path", "").startswith("repo/.git/")
        }
        self.assertTrue(all(tag is not None for tag in git_tags))
        # Also ensure project_root is present for repo files
        repo_roots = {
            item.get("project_root")
            for item in data["results"]
            if item.get("path", "").startswith("repo/") and ".git/" not in item.get("path", "")
        }
        self.assertTrue(len(repo_roots) == 1)
        self.assertIsNotNone(next(iter(repo_roots)))

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
        upload = SimpleUploadedFile("multi.zip", zip_bytes, content_type="application/zip")
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        r1_tags = {
            item.get("project_tag")
            for item in data["results"]
            if item.get("path", "").startswith("r1/") and ".git/" not in item.get("path", "")
        }
        r2_tags = {
            item.get("project_tag")
            for item in data["results"]
            if item.get("path", "").startswith("r2/") and ".git/" not in item.get("path", "")
        }

        # Each repo should have at least one tag, and those tags should not be the same
        self.assertTrue(len(r1_tags) == 1, f"Expected one tag for r1, got {r1_tags}")
        self.assertTrue(len(r2_tags) == 1, f"Expected one tag for r2, got {r2_tags}")
        self.assertNotEqual(next(iter(r1_tags)), next(iter(r2_tags)))

        git_tags_r1 = {
            item.get("project_tag")
            for item in data["results"]
            if item.get("path", "").startswith("r1/.git/")
        }
        git_tags_r2 = {
            item.get("project_tag")
            for item in data["results"]
            if item.get("path", "").startswith("r2/.git/")
        }
        self.assertTrue(all(tag is not None for tag in git_tags_r1))
        self.assertTrue(all(tag is not None for tag in git_tags_r2))
        # Ensure project_root exists and differs for r1 and r2 files
        r1_roots = {
            item.get("project_root")
            for item in data["results"]
            if item.get("path", "").startswith("r1/") and ".git/" not in item.get("path", "")
        }
        r2_roots = {
            item.get("project_root")
            for item in data["results"]
            if item.get("path", "").startswith("r2/") and ".git/" not in item.get("path", "")
        }
        self.assertTrue(len(r1_roots) == 1)
        self.assertTrue(len(r2_roots) == 1)
        self.assertNotEqual(next(iter(r1_roots)), next(iter(r2_roots)))
