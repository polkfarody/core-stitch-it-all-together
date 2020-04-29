from django.db import models


class TimestampedModel(models.Model):
    # A timestamp representing when this object was created.
    created = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        ordering = ['-created', '-updated']
