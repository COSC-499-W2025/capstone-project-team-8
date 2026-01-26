# Generated migration for incremental upload support

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_portfolio_portfolioproject_portfolio_projects_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='base_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                  related_name='incremental_versions', to='app.project',
                                  help_text='Points to the original project if this is an incremental update'),
        ),
        migrations.AddField(
            model_name='project',
            name='version_number',
            field=models.IntegerField(default=1, help_text='Version number for incremental updates'),
        ),
        migrations.AddField(
            model_name='project',
            name='is_incremental_update',
            field=models.BooleanField(default=False, 
                                    help_text='True if this project is an incremental update to another project'),
        ),
        migrations.AddField(
            model_name='project',
            name='incremental_upload_session',
            field=models.CharField(max_length=100, blank=True, db_index=True,
                                 help_text='Session ID to group related incremental uploads together'),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='supports_incremental_updates',
            field=models.BooleanField(default=True, 
                                    help_text='Whether this portfolio accepts incremental updates'),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='last_incremental_upload',
            field=models.DateTimeField(blank=True, null=True,
                                     help_text='Timestamp of the last incremental upload'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['user', 'base_project', 'version_number'], 
                             name='project_version_idx'),
        ),
    ]