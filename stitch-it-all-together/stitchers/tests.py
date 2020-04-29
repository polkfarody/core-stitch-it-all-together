from django.test import TestCase

from django.contrib.auth.models import User
from .models import Stitcher


class StitchersTestCase(TestCase):

    def setUp(self):
        self.test_auth_user = User.objects.create(
            first_name='Luke',
            last_name='Luke',
            username='luke',
            password='lukepassword'
        )

        self.test_stitcher = Stitcher.objects.create(
            user=self.test_auth_user,
            motto=None
        )

    def test_get_motto_uppercase_none(self):
        self.assertEqual(self.test_stitcher.get_motto_uppercase(), '')

    def test_get_motto_uppercase_values(self):
        motto = "This is a motto"

        self.test_stitcher.motto = motto

        self.assertEqual(motto.upper(), self.test_stitcher.get_motto_uppercase())
