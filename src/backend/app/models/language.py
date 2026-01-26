from django.db import models

class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General Purpose'),
            ('web', 'Web Development'),
            ('data', 'Data Science'),
            ('mobile', 'Mobile'),
            ('system', 'System Programming'),
            ('other', 'Other')
        ],
        default='general'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'programming_languages'
        ordering = ['name']
    def __str__(self):
        return self.name

class Framework(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=30,
        choices=[
            ('web_frontend', 'Web Frontend'),
            ('web_backend', 'Web Backend'),
            ('mobile', 'Mobile'),
            ('data_science', 'Data Science'),
            ('testing', 'Testing'),
            ('ui_library', 'UI Library'),
            ('build_tool', 'Build Tool'),
            ('database', 'Database/ORM'),
            ('other', 'Other')
        ],
        default='other'
    )
    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='frameworks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'frameworks'
        ordering = ['name']
    def __str__(self):
        return self.name