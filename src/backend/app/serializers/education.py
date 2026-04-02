from rest_framework import serializers
from app.models.education import Education

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 
            'institution', 
            'degree', 
            'major', 
            'location', 
            'start_date', 
            'end_date', 
            'description', 
            'currently_studying', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
