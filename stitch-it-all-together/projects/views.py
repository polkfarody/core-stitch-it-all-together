from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from projects.models import Project
from projects.permissions import IsOwnerOrReadOnly
from projects.serializers import ProjectSerializer


class ProjectViewSet(ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.stitcher)
