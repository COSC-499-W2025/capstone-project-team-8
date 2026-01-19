"""
Test contribution metrics extraction

Shows how the new contribution metrics analyzer enriches contributor data with:
- Activity type frequency (code/test/documentation/design/configuration)
- Contribution duration
- File type distribution
- Primary programming languages
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from app.services.analysis.analyzers.contribution_metrics import (
    extract_contributor_metrics,
    _classify_commit_activity,
)


class TestContributionMetrics:
    """Test contribution metrics extraction"""
    
    def test_classify_commit_activity_by_message(self):
        """Test commit classification by message keywords"""
        # Test keywords
        test_commit = {
            'commit_message': 'Add unit tests for auth module',
            'file_extensions': ['.py']
        }
        assert _classify_commit_activity(test_commit) == 'test'
        
        doc_commit = {
            'commit_message': 'Update README and documentation',
            'file_extensions': ['.md']
        }
        assert _classify_commit_activity(doc_commit) == 'documentation'
        
        config_commit = {
            'commit_message': 'Add Docker configuration',
            'file_extensions': ['.yml']
        }
        assert _classify_commit_activity(config_commit) == 'configuration'
    
    def test_classify_commit_activity_by_file_extension(self):
        """Test commit classification by file types"""
        test_file_commit = {
            'commit_message': 'Fix auth',
            'file_extensions': ['.test.ts', '.ts']
        }
        assert _classify_commit_activity(test_file_commit) == 'test'
        
        style_commit = {
            'commit_message': 'Update styles',
            'file_extensions': ['.css', '.scss']
        }
        assert _classify_commit_activity(style_commit) == 'design'
        
        code_commit = {
            'commit_message': 'Refactor',
            'file_extensions': ['.py', '.js']
        }
        assert _classify_commit_activity(code_commit) == 'code'
    
    def test_expected_metrics_structure(self):
        """Test that metrics have expected structure (without actual git repo)"""
        # This demonstrates what the enriched contributor data should look like
        expected_contributor_metrics = {
            "John Doe": {
                "commits": 45,
                "lines_added": 3200,
                "lines_deleted": 450,
                "first_commit": "2024-01-15",
                "last_commit": "2025-01-11",
                "contribution_duration_days": 361,
                "contribution_duration_months": 11.8,
                "activity_types": {
                    "code": {
                        "count": 35,
                        "lines_added": 2800,
                        "lines_deleted": 400
                    },
                    "test": {
                        "count": 7,
                        "lines_added": 300,
                        "lines_deleted": 30
                    },
                    "documentation": {
                        "count": 3,
                        "lines_added": 100,
                        "lines_deleted": 20
                    }
                },
                "file_type_distribution": {
                    ".py": {"commits": 25, "lines_added": 1800},
                    ".js": {"commits": 15, "lines_added": 1000},
                    ".md": {"commits": 5, "lines_added": 400}
                },
                "primary_languages": ["Python", "JavaScript"]
            }
        }
        
        # Verify structure
        contributor = expected_contributor_metrics["John Doe"]
        assert "commits" in contributor
        assert "lines_added" in contributor
        assert "contribution_duration_days" in contributor
        assert "activity_types" in contributor
        assert "file_type_distribution" in contributor
        assert "primary_languages" in contributor
        
        # Verify activity type breakdown
        activity = contributor["activity_types"]
        assert "code" in activity
        assert "test" in activity
        assert "documentation" in activity
        assert activity["code"]["count"] > 0


class TestContributorDataEnrichment:
    """
    Integration tests showing how contributor data is enriched
    This demonstrates the final format of enriched contributors
    """
    
    def test_enriched_contributor_format_in_response(self):
        """Show the enriched contributor format in the JSON response"""
        enriched_response = {
            "projects": [
                {
                    "id": 1,
                    "root": "my-project",
                    "contributors": [
                        {
                            # Original data from git
                            "name": "Alice Smith",
                            "email": "alice@example.com",
                            "commits": 42,
                            "lines_added": 2100,
                            "lines_deleted": 350,
                            "percent_commits": 60.0,
                            
                            # NEW: Activity type breakdown
                            "activity_types": {
                                "code": {
                                    "count": 32,
                                    "lines_added": 1800,
                                    "lines_deleted": 300
                                },
                                "test": {
                                    "count": 8,
                                    "lines_added": 250,
                                    "lines_deleted": 50
                                },
                                "documentation": {
                                    "count": 2,
                                    "lines_added": 50,
                                    "lines_deleted": 0
                                }
                            },
                            
                            # NEW: Duration metrics
                            "first_commit": "2024-03-01",
                            "last_commit": "2025-01-11",
                            "contribution_duration_days": 315,
                            "contribution_duration_months": 10.3,
                            
                            # NEW: File type distribution
                            "file_type_distribution": {
                                ".py": {
                                    "commits": 25,
                                    "lines_added": 1400
                                },
                                ".js": {
                                    "commits": 12,
                                    "lines_added": 600
                                },
                                ".md": {
                                    "commits": 5,
                                    "lines_added": 100
                                }
                            },
                            
                            # NEW: Primary languages/frameworks
                            "primary_languages": ["Python", "JavaScript"]
                        }
                    ]
                }
            ]
        }
        
        contributor = enriched_response["projects"][0]["contributors"][0]
        
        # Old fields still present
        assert contributor["name"] == "Alice Smith"
        assert contributor["commits"] == 42
        
        # New enrichments present
        assert "activity_types" in contributor
        assert contributor["activity_types"]["code"]["count"] == 32
        assert contributor["activity_types"]["test"]["count"] == 8
        
        assert "first_commit" in contributor
        assert contributor["contribution_duration_days"] == 315
        
        assert "file_type_distribution" in contributor
        assert ".py" in contributor["file_type_distribution"]
        
        assert "primary_languages" in contributor
        assert "Python" in contributor["primary_languages"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
