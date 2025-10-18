import io
import zipfile
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile


class UploadFolderTests(TestCase):
    def setUp(self):
        self.client = Client()

    def make_zip_bytes(self, files: dict) -> bytes:
        """Create an in-memory zip archive. files is a dict of name->content bytes or str."""
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, mode="w") as z:
            for name, content in files.items():
                data = content.encode("utf-8") if isinstance(content, str) else content
                z.writestr(name, data)
        return bio.getvalue()

    def test_get_usage(self):
        resp = self.client.get("/api/upload-folder/")
        self.assertEqual(resp.status_code, 200)

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

    def test_missing_file(self):
        resp = self.client.post("/api/upload-folder/", {})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("error", data)

    def test_non_zip_upload(self):
        txt = SimpleUploadedFile("notazip.txt", b"this is not a zip", content_type="text/plain")
        resp = self.client.post("/api/upload-folder/", {"file": txt})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("Uploaded file is not a zip archive", data.get("error", ""))

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
