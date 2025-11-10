import io
import zipfile
from types import SimpleNamespace

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch


def make_docx_bytes(text: str) -> bytes:
    """Create a minimal .docx file in-memory containing `text` as a single paragraph."""
    types_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="/word/document.xml"/>'
        '</Relationships>'
    )

    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        f'<w:p><w:r><w:t>{text}</w:t></w:r></w:p>'
        '</w:body>'
        '</w:document>'
    )

    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as z:
        z.writestr("[Content_Types].xml", types_xml)
        z.writestr("_rels/.rels", rels_xml)
        z.writestr("word/document.xml", doc_xml)
    return bio.getvalue()


def make_zip_with_files(files: dict) -> bytes:
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as z:
        for name, data in files.items():
            if isinstance(data, bytes):
                z.writestr(name, data)
            else:
                z.writestr(name, data)
    return bio.getvalue()


class ContentReadingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _post_zip(self, zip_bytes: bytes):
        upload = SimpleUploadedFile("upload.zip", zip_bytes, content_type="application/zip")

        # minimal analyzers and classifier used by the view
        analyzers = SimpleNamespace()
        analyzers.discover_projects = lambda r: {}
        analyzers.analyze_image = lambda p: {"type": "image", "path": str(p), "size": 0}
        analyzers.analyze_content = lambda p: {"type": "content", "path": str(p), "length": 0}
        analyzers.analyze_code = lambda p: {"type": "code", "path": str(p), "lines": 0}

        classifier = SimpleNamespace(classify_project=lambda p: {"classification": "writing", "confidence": 0.9})

        def import_side(name):
            if name == "app.services.analyzers":
                return analyzers
            if name == "app.services.project_classifier":
                return classifier
            if name == "app.services.gitFinder":
                return SimpleNamespace(get_git_contributors=lambda p: {"contributors": {}})
            return SimpleNamespace()

        with patch("importlib.import_module", side_effect=import_side):
            resp = self.client.post(
                "/api/upload-folder/",
                {"file": upload, "consent_scan": "1"},
                format="multipart",
            )

        return resp

    def test_txt_and_docx_content_reading(self):
        txt = "This is a plain text essay. It should be read."
        docx_text = "This is a docx essay. It should also be read."

        docx_bytes = make_docx_bytes(docx_text)
        zip_bytes = make_zip_with_files({"essay.txt": txt, "essay.docx": docx_bytes})

        resp = self._post_zip(zip_bytes)
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()

        # Find content files across projects
        found_txt = False
        found_docx = False
        for proj in payload.get("projects", []):
            for f in proj.get("files", {}).get("content", []):
                name = f.get("path")
                if name == "essay.txt":
                    found_txt = True
                    self.assertIn("text", f)
                    self.assertIn("plain text essay", f.get("text"))
                if name == "essay.docx":
                    found_docx = True
                    self.assertIn("text", f)
                    self.assertIn("docx essay", f.get("text"))

        self.assertTrue(found_txt, "essay.txt not present in response content files")
        self.assertTrue(found_docx, "essay.docx not present in response content files")
