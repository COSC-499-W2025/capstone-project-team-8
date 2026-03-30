from rest_framework import serializers
from app.models.award import Award

class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = [
            'id', 
            'title', 
            'issuer', 
            'date_received', 
            'description', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
