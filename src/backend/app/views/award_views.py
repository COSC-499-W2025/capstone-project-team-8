from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from app.models import Award
from app.serializers import AwardSerializer

@extend_schema_view(
    list=extend_schema(description="List all awards for the authenticated user", tags=["Awards"]),
    create=extend_schema(description="Create a new award entry for the authenticated user", tags=["Awards"]),
    retrieve=extend_schema(description="Retrieve a specific award", tags=["Awards"]),
    update=extend_schema(description="Update a specific award", tags=["Awards"]),
    partial_update=extend_schema(description="Partially update a specific award", tags=["Awards"]),
    destroy=extend_schema(description="Delete a specific award", tags=["Awards"])
)
class AwardViewSet(viewsets.ModelViewSet):
    serializer_class = AwardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Award.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
