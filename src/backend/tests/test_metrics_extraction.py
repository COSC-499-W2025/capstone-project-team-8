"""
Quick test to verify contribution metrics are being extracted
Run this to debug name matching and metrics extraction
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'backend'))
django.setup()

from app.services.analysis.analyzers.contribution_metrics import extract_contributor_metrics

# Test on a sample git repo
test_repo = Path("/path/to/test/repo")  # Replace with actual test repo

if test_repo.exists():
    print(f"Testing metrics extraction on: {test_repo}")
    metrics = extract_contributor_metrics(test_repo, [])
    
    print(f"\nFound metrics for {len(metrics)} contributors:")
    for name, data in metrics.items():
        print(f"\n{name}:")
        print(f"  - Commits: {data.get('commits')}")
        print(f"  - Activity types: {list(data.get('activity_types', {}).keys())}")
        print(f"  - Duration: {data.get('contribution_duration_months')} months")
        print(f"  - Languages: {data.get('primary_languages', [])}")
else:
    print("Test repo not found. Update the path to point to a real git repository.")
