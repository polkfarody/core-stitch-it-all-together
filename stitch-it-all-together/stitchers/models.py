from django.db import models
from django.db.models import signals
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

    def __str__(self):
        return self.user.username

    def get_motto_uppercase(self):
        return self.motto.upper() if self.motto is not None else ''

    @classmethod
    def create_stitcher_from_user(cls, user: User) -> 'Stitcher':
        """
        :param User user:
        :return Stitcher:
        """
        if not hasattr(user, 'stitcher'):
            stitcher = cls.objects.get_or_create(
                user=user
            )
        else:
            stitcher = user.stitcher

        return stitcher

    @classmethod
    def create_stitcher_signal_handler(cls, sender: type, instance: User, *_, **__):
        if sender is User:
            cls.create_stitcher_from_user(user=instance)


signals.post_save.connect(Stitcher.create_stitcher_signal_handler, sender=User)
