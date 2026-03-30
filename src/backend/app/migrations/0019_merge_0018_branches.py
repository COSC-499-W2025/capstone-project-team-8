# Merge migration: two parallel 0018 migrations branched from 0017.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0018_award_education"),
        ("app", "0018_user_skill_expertises"),
    ]

    operations = []
