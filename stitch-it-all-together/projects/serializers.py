from rest_framework import serializers

from projects.models import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedIdentityField(source='owner.user', view_name='stitcher-detail')
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'type_display', 'max_stitches', 'owner']
