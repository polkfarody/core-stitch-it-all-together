import warnings
import os

from django.db import models

from django.db import models
from django.utils.timezone import now

from core.models import StatusModel, StatusModelQuerySet, StatusModelManager
from core.models import TimestampedModel

from .utils import FileValidatorFunction


class MediaItemQuerySet(StatusModelQuerySet):

    def for_stitcher(self, stitcher):
        return self.filter(owner=stitcher)

    def for_user(self, user):
        return self.filter(owner__user=user)

    def public(self):
        return self.filter(owner__isnull=True)

    def images(self):
        return self.filter(imageasset__isnull=False)

    def audios(self):
        return self.filter(audioasset__isnull=False)

    def videos(self):
        return self.filter(videoasset__isnull=False)

    def documents(self):
        return self.filter(documentasset__isnull=False)


class MediaItemManager(StatusModelManager):

    def _get_queryset(self):
        return MediaItemQuerySet(model=self.model, using=self._db, hints=self._hints)

    # TODO: I think I can automate this to pull methods from the queryset

    def for_stitcher(self, stitcher):
        return self.get_queryset().for_stitcher(stitcher)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def public(self):
        return self.get_queryset().public()

    def images(self):
        return self.get_queryset().filter(imageasset__isnull=False)

    def audios(self):
        return self.get_queryset().filter(audioasset__isnull=False)

    def videos(self):
        return self.get_queryset().filter(videoasset__isnull=False)

    def documents(self):
        return self.get_queryset().filter(documentasset__isnull=False)


class MediaItemError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class MediaItem(StatusModel, TimestampedModel):
    """
    Model for storing media. This is a cross table inheritance model with each type
    of file allowed being a table that inherits from this one. This allows assigning
    a media item of any type to any other model without needing to juggle whether something
    is an image or a file or a video, etc.
    """

    LICENSE_TYPE_CHOICES = [
        (0, 'Copyright. All rights reserved'),
        (1, 'MIT'),
        (2, 'Creative Commons'),
        (3, 'GNU'),
        (4, 'BSD')
    ]

    asset_type_name = 'file'

    track_status_changes = False

    name = models.CharField(max_length=255)

    description = models.TextField(blank=True, null=True)

    size = models.IntegerField(help_text="The size of the file in bytes", editable=False, default=0)

    owner = models.ForeignKey(
        'stitchers.Stitcher',
        null=True,
        blank=True,
        help_text="Null allowed for things like files used in the system or a base suite of templates",
        on_delete=models.CASCADE
    )

    objects = MediaItemManager()

    @staticmethod
    def upload_to(instance, filename):
        base_dir = 'public' if not instance.owner else instance.owner.pk
        asset_type = getattr(instance, 'asset_type_name', 'files')

        timestamp = now()

        return 'uploads/{base_dir}/{asset_type}/{year}/{month}/{filename}'.format(
            base_dir=base_dir,
            asset_type=asset_type,
            filename=filename,
            year=timestamp.year,
            month=timestamp.month
        )

    @staticmethod
    def get_upload_file_validator(max_file_size=None, allowed_mimetypes=None, allowed_extensions=None):
        """
        Returns a validator function that will be used to validate uploaded files.

        A Validation error will be raised if the allowed mimetypes aren't satisfied or if the upload
        is too large.
        """
        try:
            import magic
        except ImportError:
            warnings.warn(
                "python-magic not installed. Simplified file type checking will take place. "
                "More details https://github.com/ahupp/python-magic"
            )

        allowed_mimetypes = [
            amt.lower() for amt in allowed_mimetypes
        ] if allowed_mimetypes else []

        allowed_extensions = [
            ae.lower() for ae in allowed_extensions
        ] if allowed_extensions else []

        return FileValidatorFunction(
            max_file_size=max_file_size,
            allowed_mimetypes=allowed_mimetypes,
            allowed_extensions=allowed_extensions
        )

    def __str__(self):
        return '<{} "{}">'.format(
            self.asset_type_name, self.name
        )

    def get_file_size(self):
        return 0

    def get_file_name(self):
        return id(self)

    def get_type_instance(self):
        if isinstance(self, (ImageAsset, AudioAsset, VideoAsset, DocumentAsset)):
            return self
        if hasattr(self, 'imageasset'):
            return self.imageasset
        if hasattr(self, 'videoasset'):
            return self.videoasset
        if hasattr(self, 'audioasset'):
            return self.audioasset
        if hasattr(self, 'documentasset'):
            return self.documentasset

        raise MediaItemError(
            "Orhaned Media Item: {}".format(self.pk)
        )

    def save(self, *args, **kwargs):

        if not isinstance(self, (ImageAsset, AudioAsset, VideoAsset, DocumentAsset)):
            raise MediaItemError(
                "Saving of MediaItem base item not allowed. Please use type instance"
            )

        self.size = self.get_type_instance().get_file_size()

        if not self.name:
            self.name = self.get_file_name()
        return super().save(*args, **kwargs)


class ImageAsset(MediaItem):

    asset_type_name = 'image'

    file = models.ImageField(
        upload_to=MediaItem.upload_to,
        width_field='width',
        height_field='height'
    )

    width = models.IntegerField(editable=False)
    height = models.IntegerField(editable=False)

    def get_file_size(self):
        return self.file.size

    def get_file_name(self):
        return self.file.name


class AudioAsset(MediaItem):

    ALLOWED_MIMETYPES = [
        'audio/vnd.wave',
        'audio/wav',
        'audio/wave',
        'audio/x-wav'
    ]  # TODO: Determine actual valid sets of mimetypes

    asset_type_name = 'audio'

    file = models.FileField(
        upload_to=MediaItem.upload_to,
        validators=(
            MediaItem.get_upload_file_validator(
                allowed_mimetypes=ALLOWED_MIMETYPES
            ),
        )
    )

    def get_file_size(self):
        return self.file.size

    def get_file_name(self):
        return self.file.name


class VideoAsset(MediaItem):

    ALLOWED_MIMETYPES = [
        'video/mpg',
        'video/mov',
        'application/csv',
    ]

    asset_type_name = 'video'

    file = models.FileField(
        upload_to=MediaItem.upload_to,
        validators=(
            MediaItem.get_upload_file_validator(
                allowed_mimetypes=ALLOWED_MIMETYPES
            ),
        )
    )

    def get_file_size(self):
        return self.file.size

    def get_file_name(self):
        return self.file.name


class DocumentAsset(MediaItem):

    ALLOWED_MIMETYPES = [
        'text/text',
        'application/pdf'
    ]

    asset_type_name = 'document'

    file = models.FileField(
        upload_to=MediaItem.upload_to,
        validators=(
            MediaItem.get_upload_file_validator(
                allowed_mimetypes=ALLOWED_MIMETYPES
            ),
        )
    )

    def get_file_size(self):
        return self.file.size

    def get_file_name(self):
        return self.file.name


class Project(StatusModel, TimestampedModel):

    track_status_changes = True

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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
