from django.db import models

from django.db import models

from core.models import TimestampedModel

TYPES = sorted([
    (1, 'Music'),
    (2, 'Lyrics'),
    (3, 'Joke'),
    (4, 'Story'),
])


class Project(TimestampedModel):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    type = models.SmallIntegerField(choices=TYPES, default=1)
    owner = models.ForeignKey('stitchers.Stitcher', related_name='projects', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
