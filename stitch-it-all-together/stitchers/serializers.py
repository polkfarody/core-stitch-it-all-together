from django.contrib.auth.models import User
from rest_framework import serializers

from projects.models import Project
from stitchers.models import Stitcher


class StitcherSerializer(serializers.HyperlinkedModelSerializer):
    projects = serializers.HyperlinkedRelatedField(many=True, view_name='project-detail', queryset=Project.objects.all())
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Stitcher
        fields = ['id', 'username', 'motto', 'projects']