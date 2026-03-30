from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from app.models import Education
from app.serializers import EducationSerializer

@extend_schema_view(
    list=extend_schema(description="List all education entries for the authenticated user", tags=["Education"]),
    create=extend_schema(description="Create a new education entry for the authenticated user", tags=["Education"]),
    retrieve=extend_schema(description="Retrieve a specific education entry", tags=["Education"]),
    update=extend_schema(description="Update a specific education entry", tags=["Education"]),
    partial_update=extend_schema(description="Partially update a specific education entry", tags=["Education"]),
    destroy=extend_schema(description="Delete a specific education entry", tags=["Education"])
)
class EducationViewSet(viewsets.ModelViewSet):
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Education.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
