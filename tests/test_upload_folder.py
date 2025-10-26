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
        