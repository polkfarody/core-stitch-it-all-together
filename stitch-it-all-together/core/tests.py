from datetime import datetime
from unittest import mock

from freezegun import freeze_time
from django.test import TestCase
from django.db import connection
from django.utils.timezone import now
from django.db.models import Model
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType

from .models import StatusModel, StatusChangeHistory


class AbstractModelTestCase(TestCase):
    """
    Allows testing of an abstract model by sneaking it into the django setup and teardown
    of the database.

    Subclass this and set the `abstract_model` class property to the abstract model mixin to
    be tested.
    """

    abstract_model = None
    model = None

    @classmethod
    def setUpClass(cls):
        # Create a real model from the mixin
        cls.model = ModelBase(
            "__AbstractTest" + cls.abstract_model.__name__,
            (cls.abstract_model,),
            {'__module__': cls.abstract_model.__module__}
        )

        with connection.schema_editor() as schema_editor:

            # Sneak the new model in
            schema_editor.create_model(cls.model)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        # Super teardown first so that any existing transactions are finished

        # Remove the content_type that was created to
        ContentType.objects.get_for_model(cls.model).delete()

        super().tearDownClass()

        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(cls.model)

        connection.close()


class TestStatusModel(AbstractModelTestCase):

    abstract_model = StatusModel

    def setUp(self):

        super(TestStatusModel, self).setUp()

        self.model.track_status_changes = False

        self.instance = self.model.objects.create()  # type: StatusModel

        self.instance_pk = self.instance.pk

        self.freeze_time_at = '2020-01-01 00:00:00'

        with freeze_time(self.freeze_time_at):
            self.now = now()  # Get frozen time for later

    def test_status_update_timestamp(self):

        # Mock django's now helper to return our timezone
        with freeze_time(self.freeze_time_at):
            # import datetime again to get the mock

            self.instance.status = StatusModel.STATUSES['DELETED']
            self.instance.save()

            self.assertEqual(self.instance.status_update_timestamp, self.now)

    def test_soft_delete(self):

        self.instance.delete()

        self.assertEqual(self.instance.status, StatusModel.STATUSES['DELETED'])

        # Make sure it is marked as deleted in database
        instance_from_db = self.model.objects.get(pk=self.instance_pk)

        self.assertEqual(instance_from_db.status, StatusModel.STATUSES['DELETED'])

    def test_enable(self):

        self.instance.status = StatusModel.STATUSES['SUSPENDED']  # Set to suspended to verify enabled is set again

        self.instance.save()

        self.instance.enable()

        self.assertEqual(self.instance.status, StatusModel.STATUSES['ENABLED'])

        # Fetch and check

        instance_from_db = self.model.objects.get(pk=self.instance_pk)

        self.assertEqual(instance_from_db.status, StatusModel.STATUSES['ENABLED'])

    def test_suspend(self):

        self.instance.suspend()

        self.assertEqual(self.instance.status, StatusModel.STATUSES['SUSPENDED'])

        # Fetch and check

        instance_from_db = self.model.objects.get(pk=self.instance_pk)

        self.assertEqual(instance_from_db.status, StatusModel.STATUSES['SUSPENDED'])

    def test_archive(self):

        self.instance.archive()

        self.assertEqual(self.instance.status, StatusModel.STATUSES['ARCHIVED'])

        # Fetch and check

        instance_from_db = self.model.objects.get(pk=self.instance_pk)

        self.assertEqual(instance_from_db.status, StatusModel.STATUSES['ARCHIVED'])

    def test_hard_delete(self):

        self.instance._delete()

        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.get(pk=self.instance_pk)

    def test_status_tracking_toggle(self):

        self.instance.track_status_changes = False

        self.instance.enable_status_change_tracking()

        self.assertTrue(self.instance.track_status_changes)

        self.instance.disable_status_change_tracking()

        self.assertFalse(self.instance.track_status_changes)

    def test_status_tracking_creation(self):

        # Don't use test case instance due to some weird teardown behaviour

        self.model.track_status_changes = True

        instance = self.model.objects.create(status=StatusModel.STATUSES['ENABLED'])

        instance.archive()

        # Should be one status change object
        self.assertEqual(len(instance.status_changes.all()), 1)

        status_change = instance.status_changes.all().get()

        self.assertEqual(
            status_change.status,
            StatusModel.STATUSES['ARCHIVED']
        )

        self.assertEqual(
            status_change.timestamp,
            instance.status_update_timestamp
        )

        Model.delete(instance)

    def test_status_tracking_ignore(self):
        self.model.track_status_changes = True

        instance = self.model.objects.create(status=StatusModel.STATUSES['ENABLED'])  # type: StatusModel

        instance.disable_status_change_tracking()

        instance.suspend()

        self.assertEqual(len(instance.status_changes.all()), 0)

        instance.enable_status_change_tracking()

        instance.enable()

        self.assertEqual(len(instance.status_changes.all()), 1)

        self.assertEqual(instance.status_changes.all()[0].status, StatusModel.STATUSES['ENABLED'])

        instance.suspend()

        # Most recent will be first. TEst ordering
        self.assertEqual(instance.status_changes.all()[0].status, StatusModel.STATUSES['SUSPENDED'])

        Model.delete(instance)

    def test_queryset_enabled(self):

        # Delete the test class instance so we are sure of numbers
        self.instance._delete()

        # create 5 of each status type
        for _ in range(5):
            for status in StatusModel.STATUSES.values():
                self.model.objects.create(status=status)

        self.assertEqual(len(self.model.objects.enabled()), 5)

        for instance in self.model.objects.enabled():
            self.assertEqual(instance.status, StatusModel.STATUSES['ENABLED'])

    def test_queryset_deleted(self):

        # create 5 of each status type
        for _ in range(5):
            for status in StatusModel.STATUSES.values():
                self.model.objects.create(status=status)

        self.assertEqual(len(self.model.objects.deleted()), 5)

        for instance in self.model.objects.deleted():
            self.assertEqual(instance.status, StatusModel.STATUSES['DELETED'])

    def test_queryset_suspended(self):

        # create 5 of each status type
        for _ in range(5):
            for status in StatusModel.STATUSES.values():
                self.model.objects.create(status=status)

        self.assertEqual(len(self.model.objects.suspended()), 5)

        for instance in self.model.objects.suspended():
            self.assertEqual(instance.status, StatusModel.STATUSES['SUSPENDED'])

    def test_queryset_archived(self):

        # create 5 of each status type
        for _ in range(5):
            for status in StatusModel.STATUSES.values():
                self.model.objects.create(status=status)

        self.assertEqual(len(self.model.objects.archived()), 5)

        for instance in self.model.objects.archived():
            self.assertEqual(instance.status, StatusModel.STATUSES['ARCHIVED'])

    def test_queryset_all(self):
        for _ in range(5):
            for status in StatusModel.STATUSES.values():
                self.model.objects.create(status=status)

        # Deleted shouldn't who up in all
        for instance in self.model.objects.all():
            self.assertNotEqual(instance.status, StatusModel.STATUSES['DELETED'])

        # But they should show up if teh deleted filter has been used
        qs = self.model.objects.deleted().all()

        self.assertEqual(len(qs), 5)

        for instance in qs:
            self.assertEqual(instance.status, StatusModel.STATUSES['DELETED'])

    def test_queryset_delete(self):
        self.instance._delete()

        for _ in range(5):
            for status in StatusModel.STATUSES.values():
                self.model.objects.create(status=status)

        self.assertEqual(self.model.objects.enabled().delete()[0], 5)

        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.enabled().get()

    def test_queryset_hard_delete(self):

        for _ in range(5):
            for status in StatusModel.STATUSES.values():
                self.model.objects.create(status=status)

        self.assertGreater(self.model.objects.suspended().count(), 0)

        self.model.objects.suspended()._delete()

        self.assertEqual(self.model.objects.suspended().count(), 0)

    def test_queryset_update_tracked_changes(self):
        self.instance.delete()

        self.model.track_status_changes = True

        for _ in range(5):
            for status in StatusModel.STATUSES.values():
                self.model.objects.create(status=status)

        # Clear the slate of state changes for test
        StatusChangeHistory.objects.all().delete()

        # Update enabled to archived
        enabled_pks = list(self.model.objects.enabled().values_list('pk', flat=True))

        with freeze_time(self.freeze_time_at):
            self.model.objects.enabled().update(status=StatusModel.STATUSES['ARCHIVED'])

        self.assertEqual(
            self.model.objects.archived().filter(pk__in=enabled_pks).count(),
            len(enabled_pks)
        )

        # They should all have one status change
        for instance in self.model.objects.filter(pk__in=enabled_pks):
            self.assertEqual(instance.status_changes.all().count(), 1)
            self.assertEqual(instance.status_update_timestamp, self.now)

        # Update the suspended to be suspeded
        suspended_pks = list(self.model.objects.suspended().values_list('pk', flat=True))

        self.model.objects.suspended().update(status=StatusModel.STATUSES['SUSPENDED'])

        # There shouldn't be any history
        for instance in self.model.objects.filter(pk__in=suspended_pks):
            self.assertEqual(instance.status_changes.all().count(), 0)

        self.model.objects.all()._delete()




