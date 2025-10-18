import zipfile
import tempfile
import os
from pathlib import Path

from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .analyzers import analyze_image, analyze_content, analyze_code

 # These are the categories that a file will be classified as based off its extension
 # The current system is expecting a zip files to be uploaded
 # After these are scanned they would get sent to a respective analyzer
 # What's currently missing is a way for multiple files to be categorized as a project, this just analyzes all file types individually.
 # In it's state it can check for nested files as well.
 
EXT_IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}
EXT_CODE = {
	".py", ".pyw", ".pyi",
	".js", ".jsx", ".mjs", ".cjs",
	".ts", ".tsx",
	".java",
	".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hh",
	".cs",
	".go",
	".rs",
	".php", ".php3", ".php4", ".php5", ".phtml",
	".rb",
	".swift",
	".kt", ".kts",
	".scala", ".sc",
	".sh", ".bash", ".zsh",
	".ps1", ".psm1", ".bat", ".cmd",
	".pl", ".pm",
	".r",
	".jl",
	".hs", ".lhs",
	".erl", ".ex", ".exs",
	".fs", ".fsi",
	".vb",
	".sql",
	".asm", ".s",
	".groovy",
	".dart",
	".lua",
    ".html", ".htm", ".css",
    ".json", ".xml",
}
EXT_CONTENT = {".txt", ".md", ".doc", ".docx", ".pdf"}

# Returns based of found extension for file
def classify_file(path: Path):
	ext = path.suffix.lower()
	if ext in EXT_IMAGE:
		return "image"
	if ext in EXT_CODE:
		return "code"
	if ext in EXT_CONTENT:
		return "content"
	return "unknown"

# this is where files are uploaded and analyzed
class UploadFolderView(APIView):
	parser_classes = (MultiPartParser, FormParser)

	def post(self, request, format=None):
		"""Accept a ZIP file upload representing a folder. Extract and analyze files."""
		upload = request.FILES.get("file")
		if not upload:
			return JsonResponse({"error": "No file provided. Use 'file' form field."}, status=400)

		# Verify zip
		if not zipfile.is_zipfile(upload):
			return JsonResponse({"error": "Uploaded file is not a zip archive."}, status=400)

		results = []
		with tempfile.TemporaryDirectory() as tmpdir:
			tmpdir_path = Path(tmpdir)
			# write uploaded file to disk first
			archive_path = tmpdir_path / "upload.zip"
			with open(archive_path, "wb") as f:
				for chunk in upload.chunks():
					f.write(chunk)

			with zipfile.ZipFile(archive_path, "r") as z:
				z.extractall(tmpdir)

			for root, _, files in os.walk(tmpdir):
				for fname in files:
					fpath = Path(root) / fname
					kind = classify_file(fpath)
					if kind == "image":
						res = analyze_image(fpath)
					elif kind == "code":
						res = analyze_code(fpath)
					elif kind == "content":
						res = analyze_content(fpath)
					else:
						res = {"type": "unknown", "path": str(fpath)}
					results.append(res)

		return JsonResponse({"results": results})

	def get(self, request, format=None):
		"""Return a usage help message. If the client accepts HTML, return a simple upload form for manual testing."""
		accept = request.META.get("HTTP_ACCEPT", "")
		usage = {
			"endpoint": "/api/upload-folder/",
			"method": "POST",
			"field": "file (zip archive)",
			"description": "Upload a zip file containing a folder of files. The server will extract and analyze files by type (image/content/code).",
		}

		if "text/html" in accept:
			html = """
			<html>
			  <body>
			    <h1>Upload Folder</h1>
			    <form method="post" enctype="multipart/form-data">
			      <input type="file" name="file" accept=".zip" />
			      <button type="submit">Upload</button>
			    </form>
			    <p>Note: Use POST with form field 'file' containing a zip archive.</p>
			  </body>
			</html>
			"""
			return HttpResponse(html)

		return JsonResponse({"usage": usage})
