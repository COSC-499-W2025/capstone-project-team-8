from django.db import models
from app.models.user import User

class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education_history')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, blank=True)
    major = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    currently_studying = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'education'
        ordering = ['-end_date', '-start_date']
        indexes = [
            models.Index(fields=['user', '-end_date']),
        ]

    def __str__(self):
        return f"{self.institution} ({self.user.username})"
