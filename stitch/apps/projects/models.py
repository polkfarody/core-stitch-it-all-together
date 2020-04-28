from django.db import models

from django.db import models

TYPES = sorted([
    (1, 'Music'),
    (2, 'Lyrics'),
    (3, 'Joke'),
    (4, 'Story'),
])


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    type = models.SmallIntegerField(choices=TYPES, default=1)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='projects', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)

    class Meta:
        ordering = ['created']
