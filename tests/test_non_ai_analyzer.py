"""
Tests for the non-AI analyzer service
"""

import os
import sys
from django.test import TestCase

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.non_ai_analyzer import (
    generate_resume_items,
    generate_summary,
    generate_statistics,
    generate_non_ai_analysis
)


class NonAIAnalyzerTests(TestCase):
    """Test suite for non-AI analysis generation"""

    def setUp(self):
        """Set up test data"""
        self.sample_project_data = {
            "source": "zip_file",
            "projects": [
                {
                    "id": 1,
                    "root": "my-web-app",
                    "classification": {
                        "type": "coding",
                        "confidence": 0.85,
                        "features": {
                            "total_files": 15,
                            "code": 10,
                            "text": 3,
                            "image": 2
                        },
                        "languages": ["JavaScript", "Python", "HTML", "CSS"],
                        "frameworks": ["React", "Django"]
                    },
                    "files": {
                        "code": [
                            {"path": "app.js", "lines": 250},
                            {"path": "main.py", "lines": 180},
                            {"path": "index.html", "lines": 50}
                        ],
                        "content": [
                            {"path": "README.md", "length": 500}
                        ],
                        "image": [
                            {"path": "logo.png", "size": 10000}
                        ],
                        "unknown": []
                    },
                    "contributors": [
                        {
                            "name": "John Doe",
                            "email": "john@example.com",
                            "commits": 25,
                            "lines_added": 1200,
                            "lines_deleted": 150,
                            "percent_commits": 100
                        }
                    ]
                },
                {
                    "id": 2,
                    "root": "data-analysis",
                    "classification": {
                        "type": "coding",
                        "confidence": 0.75,
                        "features": {
                            "total_files": 8,
                            "code": 6,
                            "text": 2,
                            "image": 0
                        },
                        "languages": ["Python", "R"],
                        "frameworks": ["Pandas", "NumPy"]
                    },
                    "files": {
                        "code": [
                            {"path": "analysis.py", "lines": 320},
                            {"path": "visualization.py", "lines": 150}
                        ],
                        "content": [
                            {"path": "report.md", "length": 800}
                        ],
                        "image": [],
                        "unknown": []
                    },
                    "contributors": [
                        {
                            "name": "Jane Smith",
                            "email": "jane@example.com",
                            "commits": 15,
                            "lines_added": 800,
                            "lines_deleted": 50,
                            "percent_commits": 100
                        }
                    ]
                }
            ],
            "overall": {
                "classification": "coding",
                "confidence": 0.80,
                "totals": {
                    "projects": 2,
                    "files": 23,
                    "code_files": 16,
                    "text_files": 5,
                    "image_files": 2
                },
                "languages": ["JavaScript", "Python", "HTML", "CSS", "R"],
                "frameworks": ["React", "Django", "Pandas", "NumPy"]
            }
        }

    def test_generate_resume_items(self):
        """Test resume item generation"""
        resume_items = generate_resume_items(self.sample_project_data)
        
        self.assertEqual(len(resume_items), 2)
        
        # Check first project
        item1 = resume_items[0]
        self.assertEqual(item1["project_id"], 1)
        self.assertEqual(item1["project_name"], "my-web-app")
        self.assertGreater(len(item1["bullets"]), 0)
        self.assertIn("Developed", item1["bullets"][0])
        
        # Check that bullets contain relevant information
        bullets_text = " ".join(item1["bullets"])
        self.assertIn("JavaScript", bullets_text)
        self.assertIn("React", bullets_text)

    def test_generate_summary(self):
        """Test summary generation"""
        summary = generate_summary(self.sample_project_data)
        
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        self.assertIn("2 projects", summary)
        self.assertIn("23 files", summary)
        self.assertIn("JavaScript", summary)

    def test_generate_statistics(self):
        """Test statistics generation"""
        stats = generate_statistics(self.sample_project_data)
        
        self.assertIn("overview", stats)
        self.assertIn("code_metrics", stats)
        self.assertIn("technologies", stats)
        self.assertIn("contributions", stats)
        
        # Check overview
        self.assertEqual(stats["overview"]["total_projects"], 2)
        self.assertEqual(stats["overview"]["total_files"], 23)
        
        # Check code metrics
        self.assertEqual(stats["code_metrics"]["total_lines_of_code"], 950)  # 250+180+50+320+150
        self.assertGreater(stats["code_metrics"]["average_lines_per_file"], 0)
        
        # Check technologies
        self.assertIn("Python", stats["technologies"]["languages"])
        self.assertIn("React", stats["technologies"]["frameworks"])
        
        # Check contributions
        self.assertEqual(stats["contributions"]["total_commits"], 40)  # 25+15
        self.assertEqual(stats["contributions"]["total_lines_added"], 2000)  # 1200+800

    def test_generate_non_ai_analysis(self):
        """Test complete analysis generation"""
        analysis = generate_non_ai_analysis(self.sample_project_data)
        
        self.assertIn("resume_items", analysis)
        self.assertIn("summary", analysis)
        self.assertIn("statistics", analysis)
        
        self.assertEqual(len(analysis["resume_items"]), 2)
        self.assertIsInstance(analysis["summary"], str)
        self.assertIsInstance(analysis["statistics"], dict)

    def test_empty_projects(self):
        """Test with empty project data"""
        empty_data = {
            "source": "zip_file",
            "projects": [],
            "overall": {
                "classification": "unknown",
                "confidence": 0.0,
                "totals": {
                    "projects": 0,
                    "files": 0,
                    "code_files": 0,
                    "text_files": 0,
                    "image_files": 0
                }
            }
        }
        
        resume_items = generate_resume_items(empty_data)
        self.assertEqual(len(resume_items), 0)
        
        summary = generate_summary(empty_data)
        self.assertIn("No projects", summary)
        
        stats = generate_statistics(empty_data)
        self.assertEqual(stats["overview"]["total_projects"], 0)

    def test_mixed_project_types(self):
        """Test with mixed project types"""
        mixed_data = {
            "source": "zip_file",
            "projects": [
                {
                    "id": 1,
                    "root": "art-portfolio",
                    "classification": {
                        "type": "art",
                        "confidence": 0.90,
                        "features": {
                            "total_files": 20,
                            "code": 0,
                            "text": 2,
                            "image": 18
                        }
                    },
                    "files": {
                        "code": [],
                        "content": [{"path": "description.txt", "length": 200}],
                        "image": [{"path": "artwork1.png", "size": 50000}],
                        "unknown": []
                    },
                    "contributors": []
                }
            ],
            "overall": {
                "classification": "art",
                "confidence": 0.90,
                "totals": {
                    "projects": 1,
                    "files": 20,
                    "code_files": 0,
                    "text_files": 2,
                    "image_files": 18
                }
            }
        }
        
        resume_items = generate_resume_items(mixed_data)
        self.assertEqual(len(resume_items), 1)
        self.assertIn("Art/Design Project", resume_items[0]["bullets"][0])
        
        summary = generate_summary(mixed_data)
        self.assertIn("art/design", summary.lower())

