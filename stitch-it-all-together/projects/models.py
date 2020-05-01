from django.db import models

from django.db import models
from softdelete.models import SoftDeleteModel

from core.models import TimestampedModel


class Project(SoftDeleteModel, TimestampedModel):
    PROJECT_TYPES = sorted([
        (1, 'Music'),
        (2, 'Lyrics'),
        (3, 'Joke'),
        (4, 'Story'),
    ])

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    type = models.SmallIntegerField(choices=PROJECT_TYPES, default=1)
    max_stitches = models.PositiveSmallIntegerField(null=True, default=None)
    is_private = models.BooleanField(default=False)
    owner = models.ForeignKey('stitchers.Stitcher', related_name='projects', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
