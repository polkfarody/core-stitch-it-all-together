from rest_framework import serializers

from projects.models import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedIdentityField(source='owner.user', view_name='stitcher-detail')
    typeName = serializers.CharField(source='get_type_display')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'typeName', 'owner']
