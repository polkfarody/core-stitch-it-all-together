from django.db import models
from django.contrib.auth.models import User


class Stitcher(models.Model):
    """
    This is the profile model. It can be used with the auth user model from Django
    to attach project specific data for users.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Add profile type attributes here

    motto = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="How does one live their life?"
    )

    def save(self, *args, **kwargs):
        super(Stitcher, self).save(*args, **kwargs)

    def get_motto_uppercase(self):
        return self.motto.upper() if self.motto is not None else ''

