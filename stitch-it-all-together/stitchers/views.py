from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from projects.models import Project
from stitchers.models import Stitcher
from stitchers.serializers import StitcherSerializer


class StitcherViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    queryset = Stitcher.objects.all()
    serializer_class = StitcherSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
