import io
import zipfile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory
from app.views.uploadFolderView import UploadFolderView
import json

def _make_zip_bytes(file_map):
	"""
	Return bytes of a zip archive containing files from file_map: {filename: content}
	"""
	buf = io.BytesIO()
	with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
		for name, content in file_map.items():
			zf.writestr(name, content)
	buf.seek(0)
	return buf.getvalue()

def test_upload_view_returns_skill_analysis_when_consent_given():
	# Build a small zip with representative files
	files = {
		"index.html": "<!DOCTYPE html><html><body><div>hello</div></body></html>",
		"app.py": "from flask import Flask\n",
		"Dockerfile": "FROM python:3.9\n",
	}
	zip_bytes = _make_zip_bytes(files)
	uploaded = SimpleUploadedFile("project.zip", zip_bytes, content_type="application/zip")

	factory = APIRequestFactory()
	data = {"file": uploaded, "consent_scan": "1"}
	request = factory.post("/api/upload-folder/", data, format="multipart")
	# Call the view
	resp = UploadFolderView.as_view()(request)
	# JsonResponse from view
	assert resp.status_code == 200
	body = json.loads(resp.content.decode())
	# skill_analysis should be present when consent_scan is true
	assert "skill_analysis" in body
	assert isinstance(body["skill_analysis"], dict)
	# Expect some fields inside skill_analysis
	assert "total_files_scanned" in body["skill_analysis"]
	assert "skills" in body["skill_analysis"]

def test_upload_view_returns_minimal_payload_when_consent_not_given():
	# Zip content doesn't matter because consent is false
	files = {"readme.txt": "just text"}
	zip_bytes = _make_zip_bytes(files)
	uploaded = SimpleUploadedFile("project.zip", zip_bytes, content_type="application/zip")

	factory = APIRequestFactory()
	data = {"file": uploaded}  # no consent_scan
	request = factory.post("/api/upload-folder/", data, format="multipart")
	resp = UploadFolderView.as_view()(request)
	assert resp.status_code == 200
	body = json.loads(resp.content.decode())
	# minimal payload should indicate scan not performed and not include skill_analysis
	assert body.get("scan_performed") is False or body.get("scan_performed") == False
	assert "skill_analysis" not in body

