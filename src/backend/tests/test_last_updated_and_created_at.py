from django.test import TestCase
from django.utils import timezone
import datetime as dt

from app.services.database_service import ProjectDatabaseService
from app.models import User, Project

class LastUpdatedAndCreatedAtTests(TestCase):
    def setUp(self):
        # create a user with the project's custom manager
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass")

    def test_created_at_defaults_to_now_when_missing_and_last_updated_applied(self):
        service = ProjectDatabaseService()
        # Prepare analysis_data without created_at but with analysis_meta.last_updated
        iso_last = "2022-01-02T03:04:05+00:00"
        analysis_data = {
            "projects": [
                {"id": 1, "root": "proj", "classification": {}, "files": {"code": [], "content": [], "image": [], "unknown": []}, "contributors": []}
            ],
            "overall": {},
            "analysis_meta": {
                "last_updated": {
                    "projects": [
                        {"project_root": "proj", "project_tag": 1, "last_updated": iso_last}
                    ],
                    "overall_last_updated": iso_last
                }
            }
        }

        projects = service.save_project_analysis(user=self.user, analysis_data=analysis_data, upload_filename="u.zip")
        self.assertEqual(len(projects), 1)
        saved = Project.objects.get(pk=projects[0].id)

        # created_at should be set (not None) and be recent (within a minute)
        self.assertIsNotNone(saved.created_at)
        delta = timezone.now() - saved.created_at
        self.assertTrue(delta.total_seconds() < 60, f"created_at not recent: {saved.created_at}")

        # updated_at should match last_updated ISO (allow exact equality after parsing)
        parsed = dt.datetime.fromisoformat(iso_last)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        self.assertEqual(saved.updated_at.replace(microsecond=0), parsed.replace(microsecond=0))

    def test_created_at_parsed_from_payload_unix_timestamp(self):
        service = ProjectDatabaseService()
        unix_ts = 1600000000  # corresponds to 2020-09-13...
        analysis_data = {
            "projects": [
                {"id": 2, "root": "proj2", "created_at": unix_ts, "classification": {}, "files": {"code": [], "content": [], "image": [], "unknown": []}, "contributors": []}
            ],
            "overall": {}
        }

        projects = service.save_project_analysis(user=self.user, analysis_data=analysis_data, upload_filename="u2.zip")
        self.assertEqual(len(projects), 1)
        saved = Project.objects.get(pk=projects[0].id)

        expected = dt.datetime.fromtimestamp(unix_ts, tz=dt.timezone.utc)
        # compare timestamps (allowing microsecond normalization)
        self.assertEqual(saved.created_at.replace(microsecond=0), expected.replace(microsecond=0))
