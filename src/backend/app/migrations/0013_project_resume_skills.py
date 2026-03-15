from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_portfolio_portfolioproject_portfolio_projects_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='resume_skills',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
