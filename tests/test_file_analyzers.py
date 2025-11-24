import tempfile
from pathlib import Path
import os

from django.test import TestCase

# import the analyzers module we modified
from app.services.analysis.analyzers import file_analyzers


class FileAnalyzersTests(TestCase):
    def _make_file(self, dirpath: Path, name: str, contents: str) -> Path:
        p = dirpath / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(contents, encoding="utf-8")
        return p

    def test_analyze_code_skips_small_file(self):
        """Code files with fewer than 5 lines should be marked skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            # 3-line code file
            small = self._make_file(tmpdir, "small.py", "a=1\nb=2\nprint(a+b)\n")
            res = file_analyzers.analyze_code(small)
            self.assertIsInstance(res, dict)
            self.assertTrue(res.get("skipped"), "Small code file should be skipped")
            self.assertIn("reason", res)
            self.assertEqual(res.get("reason"), "too_few_lines")

    def test_analyze_content_skips_small_text(self):
        """Content/text files with fewer than 5 lines should be marked skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            small = self._make_file(tmpdir, "note.txt", "line1\nline2\nline3\n")
            res = file_analyzers.analyze_content(small)
            self.assertIsInstance(res, dict)
            self.assertTrue(res.get("skipped"), "Small content file should be skipped")
            self.assertEqual(res.get("reason"), "too_few_lines")

    def test_analyze_code_respects_node_modules_ignore(self):
        """Files under node_modules should be ignored (skipped) even if large."""
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            # file inside node_modules with many lines
            content = "\n".join(f"line{i}" for i in range(20))
            node_file = self._make_file(tmpdir, os.path.join("node_modules", "pkg", "index.js"), content)
            res = file_analyzers.analyze_code(node_file)
            self.assertIsInstance(res, dict)
            self.assertTrue(res.get("skipped"), "Files in node_modules should be skipped")
            # skipped because of ignore, not too_few_lines
            self.assertNotEqual(res.get("reason"), "too_few_lines")
