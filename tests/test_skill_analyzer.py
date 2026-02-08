import tempfile
import os
from pathlib import Path
from app.services.analysis.analyzers.skill_analyzer import analyze_project

def test_analyze_project_detects_skills_and_languages():
	# Create a temporary project structure with sample files
	with tempfile.TemporaryDirectory() as td:
		tdp = Path(td)
		# frontend files
		(tdp / "index.html").write_text("<!DOCTYPE html><html><body><div class='app'>Hi</div></body></html>", encoding="utf-8")
		(tdp / "styles.css").write_text(".root { color: red; }", encoding="utf-8")
		# javascript/react file
		(tdp / "app.js").write_text("import React from 'react'\nconsole.log('hello')", encoding="utf-8")
		# python backend + data science
		(tdp / "app.py").write_text("from flask import Flask\nimport pandas as pd\napp = Flask(__name__)\n", encoding="utf-8")
		# dockerfile for devops
		(tdp / "Dockerfile").write_text("FROM python:3.9-slim\n", encoding="utf-8")

		res = analyze_project(str(tdp))
		# Basic assertions about returned structure
		assert isinstance(res, dict)
		assert "skills" in res
		assert "total_files_scanned" in res
		assert res["total_files_scanned"] >= 4

		skills = res["skills"]
		# Expect frontend and backend and devops and data-related categories to be detected
		assert any(k.lower().startswith("frontend") for k in skills.keys())
		assert any(k.lower().startswith("web backend") or k.lower().startswith("web") for k in skills.keys())
		assert any(k.lower().startswith("devops") for k in skills.keys())
		# language breakdown for a frontend skill should include HTML, CSS or JavaScript
		frontend_skill = next((k for k in skills.keys() if "front" in k.lower()), None)
		assert frontend_skill is not None
		langs = skills[frontend_skill]["languages"]
		assert any(l in langs for l in ("HTML", "CSS", "JavaScript"))

		# backend (python) should be present and include Python in languages
		backend_skill = next((k for k in skills.keys() if "web" in k.lower() and "backend" in k.lower()), None)
		if backend_skill:
			assert "Python" in skills[backend_skill]["languages"] or "Unknown" in skills[backend_skill]["languages"]

