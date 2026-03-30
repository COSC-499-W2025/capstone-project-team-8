import io
import zipfile
from types import SimpleNamespace

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch


def make_zip_bytes(files: dict) -> bytes:
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return bio.getvalue()


class UploadConsentOrderingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _make_upload(self, files):
        data = make_zip_bytes(files)
        return SimpleUploadedFile("upload.zip", data, content_type="application/zip")

    def test_scan_declined_returns_minimal_payload_and_flags_first(self):
        """If user does not give scan consent (default unchecked) the server skips scanning and returns minimal payload with send_to_llm/scan_performed first."""
        uploaded = self._make_upload({"file.txt": "hello"})

        # Patch importlib.import_module to avoid running analyzers; view will short-circuit before using them
        with patch("importlib.import_module") as imock:
            # Ensure any import returns a simple namespace (not used for skipped scan)
            imock.return_value = SimpleNamespace()

            resp = self.client.post(
                "/api/upload-folder/",
                {"file": uploaded},
                format="multipart",
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()

        # Confirm the first keys are send_to_llm then scan_performed (insertion order)
        keys = list(payload.keys())
        self.assertGreaterEqual(len(keys), 2)
        self.assertEqual(keys[0], "send_to_llm")
        self.assertEqual(keys[1], "scan_performed")

        # Scan should not have been performed
        self.assertFalse(payload.get("scan_performed"))
        self.assertIn("overall", payload)
        self.assertEqual(payload["overall"].get("classification"), "skipped")

    def test_scan_performed_and_ordering_when_consent_given(self):
        """When consent_scan is provided, scanning is performed and ordering still puts flags first."""
        uploaded = self._make_upload({"docs/readme.md": "hi", "code/main.py": "print(1)"})

        # Build fake analyzers and classifier to control output
        analyzers = SimpleNamespace()

        def fake_discover_projects(root):
            return {}  # no git projects discovered for this test

        def fake_analyze_content(p):
            return {"type": "content", "path": str(p), "length": 2}

        def fake_analyze_code(p):
            return {"type": "code", "path": str(p), "lines": 1}

        analyzers.discover_projects = fake_discover_projects
        analyzers.analyze_image = lambda p: {"type": "image", "path": str(p), "size": 0}
        analyzers.analyze_content = fake_analyze_content
        analyzers.analyze_code = fake_analyze_code

        classifier = SimpleNamespace()
        classifier.classify_project = lambda p: {"classification": "mixed", "confidence": 0.85}

        # gitFinder not needed for this test, but patch importlib to return appropriate modules
        def import_side_effect(name):
            if name == "app.services.analyzers":
                return analyzers
            if name == "app.services.classifiers.project_classifier":
                return classifier
            if name == "app.services.analysis.analyzers.git_contributions":
                return SimpleNamespace(get_git_contributors=lambda p: {"contributors": {}})
            return SimpleNamespace()

        with patch("importlib.import_module", side_effect=import_side_effect):
            resp = self.client.post(
                "/api/upload-folder/",
                {"file": uploaded, "consent_scan": "1"},
                format="multipart",
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()

        # Confirm flags ordering and scan_performed true
        keys = list(payload.keys())
        self.assertEqual(keys[0], "send_to_llm")
        self.assertEqual(keys[1], "scan_performed")
        self.assertTrue(payload.get("scan_performed"))

        # Overall classification should match classifier result
        self.assertIn("overall", payload)
        self.assertEqual(payload["overall"].get("classification"), "mixed")

    def test_consent_send_to_llm_flag_reflected_true(self):
        """When consent_send_llm is provided, send_to_llm top-level flag is True."""
        uploaded = self._make_upload({"a.txt": "x"})

        analyzers = SimpleNamespace(discover_projects=lambda r: {})
        analyzers.analyze_image = lambda p: {"type": "image", "path": str(p), "size": 0}
        analyzers.analyze_content = lambda p: {"type": "content", "path": str(p), "length": 1}
        analyzers.analyze_code = lambda p: {"type": "code", "path": str(p), "lines": 1}

        classifier = SimpleNamespace(classify_project=lambda p: {"classification": "code", "confidence": 0.5})

        def import_side(name):
            if name == "app.services.analyzers":
                return analyzers
            if name == "app.services.classifiers.project_classifier":
                return classifier
            if name == "app.services.analysis.analyzers.git_contributions":
                return SimpleNamespace(get_git_contributors=lambda p: {"contributors": {}})
            return SimpleNamespace()

        with patch("importlib.import_module", side_effect=import_side):
            resp = self.client.post(
                "/api/upload-folder/",
                {"file": uploaded, "consent_scan": "1", "consent_send_llm": "1"},
                format="multipart",
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertTrue(payload.get("send_to_llm"))
