from django.test import TestCase

from django.contrib.auth.models import User

from stitchers.models import Stitcher
from .models import Project


class ProjectsTestCase(TestCase):

    def setUp(self):
        self.test_auth_user = User.objects.create(
            first_name='Polk',
            last_name='Farody',
            username='polkfarody',
            password='wouldnt you like to know'
        )

        self.test_stitcher = Stitcher.objects.create(
            user=self.test_auth_user,
            motto='Two ts and two os'
        )

        self.test_project = Project.objects.create(
            title='Testing',
            description='Hello World of Testing...',
            type=1,
            owner=self.test_stitcher
        )

    def test_get_type_name_value(self):
        self.assertEqual(self.test_project.get_type_name(), 'Music')
