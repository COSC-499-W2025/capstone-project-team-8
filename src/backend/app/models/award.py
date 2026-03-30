from django.db import models
from app.models.user import User

class Award(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='awards')
    title = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255, blank=True)
    date_received = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'awards'
        ordering = ['-date_received']
        indexes = [
            models.Index(fields=['user', '-date_received']),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.username})"
