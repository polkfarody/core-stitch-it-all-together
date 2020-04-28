from rest_framework import generics
from stitch.apps.projects.models import Project
from stitch.apps.projects.serializers import ProjectSerializer


class ProjectList(generics.ListCreateAPIView):
    """
    List all code projects, or create a new project.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a code project.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
