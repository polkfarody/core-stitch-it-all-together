from django.utils.timezone import now
from django.db import models
from django.db.models import signals
from django.db import transaction

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class TimestampedModel(models.Model):
    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        ordering = ['-created_at', '-updated_at']


class StatusChangeHistory(models.Model):
    """
    Tracks the changes of status
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField(db_index=True)

    content_object = GenericForeignKey()

    status = models.IntegerField(db_index=True, help_text="The status changed to this value")

    # TODO: This model may be overkill, but audit trails are generally useful.
    # TODO: And this status changed auto magic can be updated to collect other things like users, etc

    timestamp = models.DateTimeField()

    class Meta:
        unique_together = (
            ('content_type', 'object_id', 'status', 'timestamp')
        )

        ordering = ('-timestamp',)

    @classmethod
    def status_change_entry(cls, instance, created=False):

        if not isinstance(instance, StatusModel) or not getattr(instance, 'track_status_changes', False):
            return

        if not instance.pk:
            return

        from_status = instance.original_status()
        status = instance.status

        if from_status == status and not created:
            return

        content_type = ContentType.objects.get_for_model(instance)

        if not content_type:
            return

        return cls.objects.get_or_create(
            content_type=content_type,
            object_id=instance.pk,
            status=status,
            timestamp=instance.status_update_timestamp
        )

    @classmethod
    def signal_handler(cls, sender, instance, raw, created, *_, **__):

        if not issubclass(sender, StatusModel):
            return

        if not instance.track_status_changes:
            return

        StatusChangeHistory.status_change_entry(instance)


signals.post_save.connect(StatusChangeHistory.signal_handler)


class StatusModelQuerySet(models.QuerySet):

    def __init__(self, *args, **kwargs):
        super(StatusModelQuerySet, self).__init__(*args, **kwargs)

        self.allow_deleted_in_all = False

    def all(self):
        if self.allow_deleted_in_all:
            return self._chain()
        return self.exclude(status=StatusModel.STATUSES['DELETED'])

    def enabled(self):
        return self.filter(status=StatusModel.STATUSES['ENABLED'])

    def deleted(self):
        qs = self.filter(status=StatusModel.STATUSES['DELETED'])
        qs.allow_deleted_in_all = True
        return qs

    def suspended(self):
        return self.filter(status=StatusModel.STATUSES['SUSPENDED'])

    def archived(self):
        return self.filter(status=StatusModel.STATUSES['ARCHIVED'])

    def delete(self):
        """Soft delete by default"""
        deleted_count = 0
        for obj in self:
            obj.delete()
            deleted_count += 1
        return deleted_count, {}  # To be same shape of a django queryset delete

    @transaction.atomic()
    def update(self, **kwargs):
        """Intercept updates to go through status change machinery if update is being updated"""
        if 'status' not in kwargs:
            return super(StatusModelQuerySet, self).update(**kwargs)

        status = kwargs.pop('status')

        # Find the items with different status and save those. Then do the update sans status
        for obj in self.exclude(status=status):
            obj.status = status
            obj.save()

        return super(StatusModelQuerySet, self).update(**kwargs)

    def _delete(self):
        """Do a DB delete"""
        return super(StatusModelQuerySet, self).delete()

    def _clone(self):
        new = super(StatusModelQuerySet, self)._clone()
        new.allow_deleted_in_all = self.allow_deleted_in_all
        return new


class StatusModelManager(models.Manager):

    def _get_queryset(self):
        return StatusModelQuerySet(model=self.model, using=self._db, hints=self._hints)

    def get_queryset(self):
        return self._get_queryset().all()

    def get(self, *args, **kwargs):
        """Make sure get can always lookup even deleted items"""
        return self._get_queryset().get(*args, **kwargs)

    def enabled(self):
        return self._get_queryset().enabled()

    def deleted(self):
        return self._get_queryset().deleted()

    def suspended(self):
        return self._get_queryset().suspended()

    def archived(self):
        return self._get_queryset().archived()


class StatusModel(models.Model):

    STATUS_CHOICES = (
        (0, 'Enabled'),
        (1, 'Deleted'),
        (2, 'Suspended'),
        (3, 'Archived')
    )

    STATUSES = {
        v.upper(): k for k, v in STATUS_CHOICES
    }

    status = models.IntegerField(
        db_index=True,
        help_text="The status of this instance",
        default=STATUSES['ENABLED'],
        choices=STATUS_CHOICES
    )

    status_update_timestamp = models.DateTimeField(
        help_text="Updated when ths status of this instance changes",
        editable=False
    )

    status_changes = GenericRelation(StatusChangeHistory)

    objects = StatusModelManager()

    all_objects = models.Manager()  # Use this to access all items including deleted

    track_status_changes = True
    """Subclasses or instance can set this to False to disable history tracking of instances"""

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store the current status on the instance so the update timestamp can be updated
        # When it changes

        self._status = self.status
        self._status_changed = None

    def save(self, *args, **kwargs):

        if self._status != self.status or not self.status_update_timestamp:
            self.status_update_timestamp = now()
            self._status_changed = self.status_update_timestamp

        resp = super(StatusModel, self).save(*args, **kwargs)

        self._status_reset()
        return resp

    def delete(self, using=None, *args, **kwargs):
        """
        'Deletes' the instance by setting the status to DELETED
        """

        self.status = self.STATUSES['DELETED']
        self.save(using=using)

        return 1, {}

    def _delete(self, *args, **kwargs):
        """Actually deletes the model through django ORM"""
        return super(StatusModel, self).delete(*args, **kwargs)

    # TODO: Should there be limitations on what statuses an object can move between?
    # TODO: EG. Can you archive a soft deleted object?

    def enable(self, using=None):
        """Sets status to ENABLED"""

        self.status = self.STATUSES['ENABLED']
        return self.save(using=using)

    def suspend(self, using=None):
        """Sets status to SUSPENDED"""

        self.status = self.STATUSES['SUSPENDED']
        return self.save(using=using)

    def archive(self, using=None):
        """Sets status to ARCHIVED"""
        self.status = self.STATUSES['ARCHIVED']
        return self.save(using=using)

    def enable_status_change_tracking(self):
        self.track_status_changes = True

    def disable_status_change_tracking(self):
        self.track_status_changes = False

    def original_status(self):
        return self._status

    def _status_reset(self):
        self._status_changed = None
        self._status = self.status


