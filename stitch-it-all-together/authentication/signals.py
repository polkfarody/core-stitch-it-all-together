from django.db.models.signals import post_save
from django.dispatch import receiver

from stitchers.models import Stitcher

from .models import User


@receiver(post_save, sender=User)
def create_related_stitcher(sender, instance, created, *args, **kwargs):
    # Check created field
    if instance and created:
        instance.stitcher = Stitcher.objects.create(user=instance)
