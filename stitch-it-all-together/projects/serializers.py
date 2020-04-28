from rest_framework import serializers

from projects.models import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedIdentityField(source='owner.user', view_name='stitcher-detail')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'owner']
