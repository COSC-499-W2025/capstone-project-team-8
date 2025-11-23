import os
import sys
import django
from pathlib import Path
from django.test import SimpleTestCase

# Add backend path (pattern follows existing tests)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from app.services.data_transformer import transform_to_new_structure  # noqa: E402


class CollaborationTagTests(SimpleTestCase):
    def test_mixed_projects_collaboration_flags(self):
        # Simulate two projects: project 1 (collaborative), project 2 (solo)
        projects_rel = {
            1: "proj_one",
            2: "proj_two",
        }
        # Minimal results list (files with project_tag)
        results = [
            {"type": "code", "path": "proj_one/file_a.py", "project_tag": 1},
            {"type": "code", "path": "proj_one/file_b.py", "project_tag": 1},
            {"type": "content", "path": "proj_two/readme.md", "project_tag": 2},
        ]

        # Git contribution data for both projects
        git_contrib_data = {
            "project_1": {
                "contributors": {
                    "Alice": {
                        "commits": 10,
                        "lines_added": 200,
                        "lines_deleted": 50,
                        "percent_of_commits": 55.0,
                        "email": "alice@example.com",
                    },
                    "Bob": {
                        "commits": 8,
                        "lines_added": 150,
                        "lines_deleted": 20,
                        "percent_of_commits": 45.0,
                    },
                },
                "total_commits": 18,
            },
            "project_2": {
                "contributors": {
                    "Carol": {
                        "commits": 12,
                        "lines_added": 400,
                        "lines_deleted": 30,
                        "percent_of_commits": 100.0,
                    }
                },
                "total_commits": 12,
            },
        }

        payload = transform_to_new_structure(
            results=results,
            projects={},              # Not used directly for this test
            projects_rel=projects_rel,
            project_classifications={},  # Classification irrelevant for collaboration flag
            git_contrib_data=git_contrib_data,
            project_timestamps=None,
            filter_username=None,
        )

        # Extract projects by id for assertions
        proj_map = {p["id"]: p for p in payload["projects"]}
        self.assertIn(1, proj_map)
        self.assertIn(2, proj_map)

        self.assertTrue(proj_map[1]["collaborative"])
        self.assertFalse(proj_map[2]["collaborative"])

        overall = payload["overall"]
        self.assertEqual(overall["collaborative_projects"], 1)
        self.assertEqual(overall["totals"]["projects"], 2)
        self.assertEqual(overall["collaboration_rate"], 0.5)
        self.assertTrue(overall["collaborative"])

    def test_all_single_author_projects_not_collaborative(self):
        projects_rel = {1: "solo_one", 2: "solo_two"}
        results = [
            {"type": "code", "path": "solo_one/a.py", "project_tag": 1},
            {"type": "code", "path": "solo_two/b.py", "project_tag": 2},
        ]
        git_contrib_data = {
            "project_1": {
                "contributors": {
                    "DevA": {"commits": 5, "lines_added": 100, "lines_deleted": 10, "percent_of_commits": 100.0}
                },
                "total_commits": 5,
            },
            "project_2": {
                "contributors": {
                    "DevB": {"commits": 7, "lines_added": 220, "lines_deleted": 15, "percent_of_commits": 100.0}
                },
                "total_commits": 7,
            },
        }

        payload = transform_to_new_structure(
            results=results,
            projects={},
            projects_rel=projects_rel,
            project_classifications={},
            git_contrib_data=git_contrib_data,
            project_timestamps=None,
            filter_username=None,
        )

        proj_map = {p["id"]: p for p in payload["projects"]}
        self.assertFalse(proj_map[1]["collaborative"])
        self.assertFalse(proj_map[2]["collaborative"])

        overall = payload["overall"]
        self.assertEqual(overall["collaborative_projects"], 0)
        self.assertEqual(overall["collaboration_rate"], 0.0)
        self.assertFalse(overall["collaborative"])

    def test_zero_commit_contributors_not_collaborative(self):
        projects_rel = {1: "empty"}
        results = [
            {"type": "code", "path": "empty/main.py", "project_tag": 1},
        ]
        git_contrib_data = {
            "project_1": {
                "contributors": {
                    "Ghost": {"commits": 0, "lines_added": 0, "lines_deleted": 0, "percent_of_commits": 0.0},
                    "Phantom": {"commits": 0, "lines_added": 0, "lines_deleted": 0, "percent_of_commits": 0.0},
                },
                "total_commits": 0,
            }
        }

        payload = transform_to_new_structure(
            results=results,
            projects={},
            projects_rel=projects_rel,
            project_classifications={},
            git_contrib_data=git_contrib_data,
            project_timestamps=None,
            filter_username=None,
        )

        proj_map = {p["id"]: p for p in payload["projects"]}
        self.assertFalse(proj_map[1]["collaborative"])
        overall = payload["overall"]
        self.assertEqual(overall["collaborative_projects"], 0)
        self.assertFalse(overall["collaborative"])