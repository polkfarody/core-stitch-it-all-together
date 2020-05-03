import base64
import os
import shutil

from unittest import mock

from django.test import TestCase

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.conf import settings


from stitchers.models import Stitcher
from .models import (
    Project, MediaItem, ImageAsset, VideoAsset, AudioAsset, DocumentAsset, MediaItemError, FileValidatorFunction
)

small_png = b'iVBORw0KGgoAAAANSUhEUgAAAAYAAAAECAYAAACtBE5DAAAMSmlDQ1BJQ0MgUHJvZmlsZQAASImVVwdYU8kWnltSSWiBUKSE3kQRp' \
            b'EsJoUUQkCrYCEkgocSYEETsLMsquBZURMCGrooouhZA1oq9LIq9PyyorKyLBRsqb1JA1/3ee9873zf3/jlzzn9K5t47A4BOLU8qzU' \
            b'V1AciT5MviI0JYE1LTWKTHAAGGgAy8gROPL5ey4+KiAZTB+9/l7XVoDeWKq5Lrn/P/VfQEQjkfACQO4gyBnJ8H8T4A8BK+VJYPANE' \
            b'H6m1m5EuVeBLEBjKYIMRSJc5S4xIlzlDjKpVNYjwH4h0AkGk8niwLAO0WqGcV8LMgj/ZNiN0kArEEAB0yxIF8EU8AcSTEw/Pypikx' \
            b'tAOOGd/wZP2NM2OIk8fLGsLqWlRCDhXLpbm8mf9nO/635OUqBmPYw0ETySLjlTXDvt3MmRalxDSIeyQZMbEQ60P8XixQ2UOMUkWKy' \
            b'CS1PWrGl3NgzwATYjcBLzQKYjOIwyW5MdEafUamOJwLMVwhaKE4n5uo8V0olIclaDhrZdPiYwdxpozD1vg28mSquEr7E4qcJLaG/6' \
            b'ZIyB3kf1MkSkxR54xRC8TJMRBrQ8yU5yREqW0w2yIRJ2bQRqaIV+ZvC7GfUBIRoubHpmTKwuM19rI8+WC92EKRmBujwdX5osRIDc8O' \
            b'Pk+VvzHELUIJO2mQRyifED1Yi0AYGqauHbsklCRp6sU6pfkh8RrfV9LcOI09ThXmRij11hCbyQsSNL54YD5ckGp+PEaaH5eozhPPyOa' \
            b'NjVPngxeCaMABoYAFFHBkgGkgG4jbe5p74C/1TDjgARnIAkLgqtEMeqSoZiTwmgCKwJ8QCYF8yC9ENSsEBVD/eUirvrqCTNVsgcojB' \
            b'zyBOA9EgVz4W6HykgxFSwaPoUb8j+h8mGsuHMq5f+rYUBOt0SgGeVk6g5bEMGIoMZIYTnTCTfFA3B+PhtdgONxxH9x3MNuv9oQnhA7' \
            b'CQ8I1Qifh1lRxsey7elhgHOiEEcI1NWd8WzNuD1k98RA8APJDbpyJmwJXfDSMxMaDYGxPqOVoMldW/z3332r4pusaO4obBaUYUYIpj' \
            b't97ajtrew6xKHv6bYfUuWYM9ZUzNPN9fM43nRbAe9T3lthCbC92GjuGncUOYs2AhR3BWrAL2CElHlpFj1WraDBavCqfHMgj/kc8nia' \
            b'mspNytwa3brdP6rl8YaHy/Qg406QzZeIsUT6LDd/8QhZXwh8xnOXu5u4GgPI7on5NvWaqvg8I89xXXfEbAAIEAwMDB7/qouEzve9HAK' \
            b'hPvuocDsPXgREAZ8r5ClmBWocrLwRABTrwiTIBFsAGOMJ63IEX8AfBIAyMBbEgEaSCKbDLIrieZWAGmA0WgFJQDpaBVaAarAebwDawE' \
            b'+wBzeAgOAZOgfPgErgG7sDV0wWeg17wFvQjCEJC6AgDMUEsETvEBXFHfJBAJAyJRuKRVCQdyUIkiAKZjfyAlCMVSDWyEalHfkUOIMeQ' \
            b's0gHcgt5gHQjr5CPKIbSUAPUHLVHR6I+KBuNQhPRyWgWOh0tQkvQJWgVWofuQJvQY+h59BraiT5H+zCAaWFMzApzxXwwDhaLpWGZmAy' \
            b'bi5VhlVgd1oi1wv/5CtaJ9WAfcCLOwFm4K1zBkXgSzsen43PxxXg1vg1vwk/gV/AHeC/+hUAnmBFcCH4ELmECIYswg1BKqCRsIewnn' \
            b'IRPUxfhLZFIZBIdiN7waUwlZhNnERcT1xJ3EY8SO4iPiH0kEsmE5EIKIMWSeKR8UilpDWkH6QjpMqmL9J6sRbYku5PDyWlkCbmYXEn' \
            b'eTj5Mvkx+Su6n6FLsKH6UWIqAMpOylLKZ0kq5SOmi9FP1qA7UAGoiNZu6gFpFbaSepN6lvtbS0rLW8tUaryXWmq9VpbVb64zWA60PNH' \
            b'2aM41Dm0RT0JbQttKO0m7RXtPpdHt6MD2Nnk9fQq+nH6ffp7/XZmiP0OZqC7TnaddoN2lf1n6hQ9Gx02HrTNEp0qnU2atzUadHl6Jr' \
            b'r8vR5enO1a3RPaB7Q7dPj6E3Si9WL09vsd52vbN6z/RJ+vb6YfoC/RL9TfrH9R8xMIYNg8PgM35gbGacZHQZEA0cDLgG2QblBjsN2g1' \
            b'6DfUNRxsmGxYa1hgeMuxkYkx7JpeZy1zK3MO8zvxoZG7ENhIaLTJqNLps9M54mHGwsdC4zHiX8TXjjyYskzCTHJPlJs0m90xxU2fT8a' \
            b'YzTNeZnjTtGWYwzH8Yf1jZsD3DbpuhZs5m8WazzDaZXTDrM7cwjzCXmq8xP27eY8G0CLbItlhpcdii25JhGWgptlxpecTyD5Yhi83K' \
            b'ZVWxTrB6rcysIq0UVhut2q36rR2sk6yLrXdZ37Oh2vjYZNqstGmz6bW1tB1nO9u2wfa2HcXOx05kt9rutN07ewf7FPuf7JvtnzkYO3' \
            b'AdihwaHO460h2DHKc71jledSI6+TjlOK11uuSMOns6i5xrnC+6oC5eLmKXtS4dwwnDfYdLhtcNv+FKc2W7Frg2uD4YwRwRPaJ4RPO' \
            b'IFyNtR6aNXD7y9Mgvbp5uuW6b3e6M0h81dlTxqNZRr9yd3fnuNe5XPege4R7zPFo8Xo52GS0cvW70TU+G5zjPnzzbPD97eXvJvBq9' \
            b'ur1tvdO9a71v+Bj4xPks9jnjS/AN8Z3ne9D3g5+XX77fHr+//F39c/y3+z8b4zBGOGbzmEcB1gG8gI0BnYGswPTADYGdQVZBvKC6o' \
            b'IfBNsGC4C3BT9lO7Gz2DvaLELcQWcj+kHccP84cztFQLDQitCy0PUw/LCmsOux+uHV4VnhDeG+EZ8SsiKORhMioyOWRN7jmXD63n' \
            b'ts71nvsnLEnomhRCVHVUQ+jnaNl0a3j0HFjx60YdzfGLkYS0xwLYrmxK2LvxTnETY/7bTxxfNz4mvFP4kfFz44/ncBImJqwPeFtY' \
            b'kji0sQ7SY5JiqS2ZJ3kScn1ye9SQlMqUjonjJwwZ8L5VNNUcWpLGiktOW1LWt/EsImrJnZN8pxUOun6ZIfJhZPPTjGdkjvl0FSdq' \
            b'bype9MJ6Snp29M/8WJ5dby+DG5GbUYvn8NfzX8uCBasFHQLA4QVwqeZAZkVmc+yArJWZHWLgkSVoh4xR1wtfpkdmb0++11ObM7Wn' \
            b'IHclNxdeeS89LwDEn1JjuTENItphdM6pC7SUmnndL/pq6b3yqJkW+SIfLK8Jd8AbtgvKBwVPyoeFAQW1BS8n5E8Y2+hXqGk8MJM55' \
            b'mLZj4tCi/6ZRY+iz+rbbbV7AWzH8xhz9k4F5mbMbdtns28knld8yPmb1tAXZCz4Pdit+KK4jc/pPzQWmJeMr/k0Y8RPzaUapfKSm/' \
            b'85P/T+oX4QvHC9kUei9Ys+lImKDtX7lZeWf5pMX/xuZ9H/Vz188CSzCXtS72WrltGXCZZdn150PJtFXoVRRWPVoxb0bSStbJs5Zt' \
            b'VU1edrRxduX41dbVidWdVdFXLGts1y9Z8qhZVX6sJqdlVa1a7qPbdWsHay+uC1zWuN19fvv7jBvGGmxsjNjbV2ddVbiJuKtj0ZHPy' \
            b'5tO/+PxSv8V0S/mWz1slWzu3xW87Ue9dX7/dbPvSBrRB0dC9Y9KOSztDd7Y0ujZu3MXcVb4b7Fbs/uPX9F+v74na07bXZ2/jPrt9t' \
            b'fsZ+8uakKaZTb3NoubOltSWjgNjD7S1+rfu/23Eb1sPWh2sOWR4aOlh6uGSwwNHio70HZUe7TmWdexR29S2O8cnHL96YvyJ9pNRJ8' \
            b'+cCj91/DT79JEzAWcOnvU7e+Ccz7nm817nmy54Xtj/u+fv+9u92psuel9sueR7qbVjTMfhy0GXj10JvXLqKvfq+Wsx1zquJ12/eW' \
            b'PSjc6bgpvPbuXeenm74Hb/nfl3CXfL7uneq7xvdr/uX07/2tXp1XnoQeiDCw8THt55xH/0/LH88aeukif0J5VPLZ/WP3N/drA7vPv' \
            b'SHxP/6Houfd7fU/qn3p+1Lxxf7Psr+K8LvRN6u17KXg68Wvza5PXWN6PftPXF9d1/m/e2/13Ze5P32z74fDj9MeXj0/4Zn0ifqj4' \
            b'7fW79EvXl7kDewICUJ+OptgIYHGhmJgCvtgJATwWAcQnuHyaqz3kqQdRnUxUC/wmrz4Iq8QKgEd6U23XOUQB2w2E/H3IHA6Dcqic' \
            b'GA9TDY2hoRJ7p4a7mosETD+H9wMBrcwBIrQB8lg0M9K8dGPi8GSZ7C4Cj09XnS6UQ4dlgQ7ASXTMWzAffyb8B7TF/lHoEz+YAAAAJ' \
            b'cEhZcwAAFiUAABYlAUlSJPAAAAIBaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm' \
            b'1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA1LjQuMCI+CiAgIDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk' \
            b'5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+CiAgICAgIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICAgICAgICAgIHht' \
            b'bG5zOmV4aWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vZXhpZi8xLjAvIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMu' \
            b'YWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDxleGlmOlBpeGVsWURpbWVuc2lvbj44PC9leGlmOlBpeGVsWURpbWVuc2lvb' \
            b'j4KICAgICAgICAgPGV4aWY6UGl4ZWxYRGltZW5zaW9uPjEyPC9leGlmOlBpeGVsWERpbWVuc2lvbj4KICAgICAgICAgPHRpZmY6T3' \
            b'JpZW50YXRpb24+MTwvdGlmZjpPcmllbnRhdGlvbj4KICAgICAgPC9yZGY6RGVzY3JpcHRpb24+CiAgIDwvcmRmOlJERj4KPC94Onh' \
            b'tcG1ldGE+CusKj3oAAAAXSURBVAgdY7SxsfnPgAUwYREDC5EuAQCmfAG7/hIvQgAAAABJRU5ErkJggg=='

small_png = base64.b64decode(small_png)


class ProjectsTestCase(TestCase):

    def setUp(self):
        self.test_auth_user = User.objects.create(
            first_name='Polk',
            last_name='Farody',
            username='polkfarody',
            password='wouldnt you like to know'
        )

        self.test_stitcher = self.test_auth_user.stitcher

        self.test_project = Project.objects.create(
            title='Testing',
            description='Hello World of Testing...',
            type=1,
            owner=self.test_stitcher
        )

    def test_get_type_display_value(self):
        self.assertEqual(self.test_project.get_type_display(), 'Music')


class MediaItemTestCase(TestCase):

    asset_classes = (ImageAsset, AudioAsset, VideoAsset, DocumentAsset)

    def setUp(self):
        self.test_media_root = os.path.join(settings.MEDIA_ROOT, '__tests__')

        self.test_auth_user_1 = User.objects.create(
            first_name='Polk',
            last_name='Farody',
            username='polkfarody',
            password='wouldnt you like to know'
        )

        self.test_stitcher_1 = self.test_auth_user_1.stitcher

        self.test_auth_user_2 = User.objects.create(
            first_name='hey',
            last_name="that's ash",
            username='ash',
            email='bluey@something.com',
            password='redheadlol'
        )

        self.test_stitcher_2 = self.test_auth_user_2.stitcher

    @staticmethod
    def get_python_magic_hack() -> mock.Mock:
        """
        If magic can be loaded, return a mocked object for its from_buffer function.

        If it's not available, just mock something that won't be used
        """
        try:
            import magic
        except ImportError:
            magic = None

        return mock.patch('magic.from_buffer' if magic else 'random.randint')

    def test_direct_media_item_save(self):

        # Disable direct saving of the underlying media item.
        media_item = MediaItem(
            size=0,
            name='File name'
        )

        with self.assertRaises(MediaItemError):
            media_item.save()

    def test_file_validator_function_max_size(self):

        file_validator = FileValidatorFunction(
            max_file_size=10,
            allowed_mimetypes=None,
            allowed_extensions=None
        )

        uploaded_file = SimpleUploadedFile(
            'example.txt',
            b'123456789'
        )  # 9 bytes

        # This should validate
        self.assertTrue(file_validator(uploaded_file))

        uploaded_file = SimpleUploadedFile(
            'example.txt',
            b'1234567891011'
        )

        # Larger than 10 bytes
        with self.assertRaises(ValidationError):
            file_validator(uploaded_file)

    def test_file_validator_function_allowed_mimetypes(self):

        file_validator = FileValidatorFunction(
            max_file_size=None,
            allowed_mimetypes=['text/plain', 'image/jpeg'],
            allowed_extensions=None
        )

        try:
            import magic
        except ImportError:
            magic = None

        # Nasty hack for computers (windows) that won't easily get python-magic installed
        # Falls back to generic type guessing
        with self.get_python_magic_hack() as mocker:
            mocker.return_value = 'text/plain'

            uploaded_file = SimpleUploadedFile(
                'example.txt',
                b'12345678'
            )
            uploaded_file.content_type = 'text/plain'

            self.assertTrue(file_validator(uploaded_file))

            uploaded_file.content_type = 'application/octet-stream'

            mocker.return_value = 'application/octet-stream'

            with self.assertRaises(ValidationError):
                file_validator(uploaded_file)

    def test_file_validator_allowed_extensions(self):

        file_validator = FileValidatorFunction(
            max_file_size=None,
            allowed_extensions=['.jpg', '.txt', '.jpeg', '.png'],
            allowed_mimetypes=None
        )

        uploaded_file = SimpleUploadedFile(
            'example.txt',
            b'12345678'
        )

        self.assertTrue(file_validator(uploaded_file))

        uploaded_file = SimpleUploadedFile(
            'example.exe',
            b'hackityhackhack'
        )

        with self.assertRaises(ValidationError):
            file_validator(uploaded_file)

    def test_auto_size_fill(self):

        uploaded_file = SimpleUploadedFile(
            'small.png',
            small_png
        )

        with self.settings(MEDIA_ROOT=self.test_media_root):
            ia = ImageAsset.objects.create(
                file=uploaded_file
            )

            self.assertEqual(ia.size, len(small_png))

    def test_auto_name_fill(self):

        uploaded_file = SimpleUploadedFile(
            'small.png',
            small_png
        )

        with self.settings(MEDIA_ROOT=self.test_media_root):
            ia = ImageAsset.objects.create(
                file=uploaded_file
            )

            self.assertEqual(ia.name, 'small.png')

    def _create_asset(self, class_, filename=None,  **kwargs):
        """
        Mocks mimetype lookups and/or uses small_png to create an Asset object
        :param class_:
        """

        assert class_ in self.asset_classes

        with self.settings(MEDIA_ROOT=self.test_media_root):
            if class_ is ImageAsset:

                    uploaded_file = SimpleUploadedFile(
                        filename if filename else 'small.png',
                        small_png
                    )

                    return ImageAsset.objects.create(
                        file=uploaded_file,
                        **kwargs
                    )
            else:

                # Find a valid mimetype from the class
                try:
                    mimetype = class_.ALLOWED_MIMETYPES[0]
                except (IndexError, AttributeError):
                    self.assertTrue(False, "{} does not have ALLOWED_MIMETYPES Specified")
                    return

                with self.get_python_magic_hack() as mocker:
                    mocker.return_value = mimetype

                    uploaded_file = SimpleUploadedFile(
                        filename if filename else 'test.{}'.format(mimetype.split('/')[-1]),
                        b'randomtextinsidethefile'
                    )

                    return class_.objects.create(
                        file=uploaded_file,
                        **kwargs
                    )

    def _create_many_assets(self, how_many, owner=None):
        """Shortcut to create a bunch of assets"""

        for i in range(how_many):
            for class_ in self.asset_classes:
                self._create_asset(class_, owner=owner)

    def test_the_create_asset_test(self):
        # Sanity test that the creation of test assets works
        for class_ in self.asset_classes:
            self.assertIsInstance(
                self._create_asset(class_),
                class_
            )

    def test_the_create_many_assets_test(self):
        # More sanity
        self._create_many_assets(10)
        for class_ in self.asset_classes:
            self.assertEqual(
                class_.objects.all().count(),
                10
            )

    def test_media_item_queryset_for_user(self):

        self._create_many_assets(10)
        self._create_many_assets(10, owner=self.test_stitcher_1)
        self._create_many_assets(5, owner=self.test_stitcher_2)

        for class_ in self.asset_classes:
            self.assertEqual(
                class_.objects.for_user(self.test_stitcher_1.user).count(),
                10
            )
            self.assertEqual(
                class_.objects.for_user(self.test_stitcher_2.user).count(),
                5
            )

    def test_media_item_queryset_for_stitcher(self):

        self._create_many_assets(10)
        self._create_many_assets(10, owner=self.test_stitcher_1)
        self._create_many_assets(5, owner=self.test_stitcher_2)

        for class_ in self.asset_classes:
            self.assertEqual(
                class_.objects.for_stitcher(self.test_stitcher_1).count(),
                10
            )
            self.assertEqual(
                class_.objects.for_stitcher(self.test_stitcher_2).count(),
                5
            )

    def test_media_item_queryset_public(self):

        self._create_many_assets(10)
        self._create_many_assets(10, owner=self.test_stitcher_1)
        self._create_many_assets(5, owner=self.test_stitcher_2)

        for class_ in self.asset_classes:
            self.assertEqual(
                class_.objects.public().count(),
                10
            )

    def test_media_item_queryset_images(self):

        self._create_many_assets(10)
        self._create_many_assets(10, owner=self.test_stitcher_1)
        self._create_many_assets(5, owner=self.test_stitcher_2)

        count = 0
        for instance in MediaItem.objects.images():
            self.assertIsInstance(instance.get_type_instance(), ImageAsset)
            count += 1

        self.assertEqual(count, 25)

    def test_media_item_queryset_audios(self):

        self._create_many_assets(10)
        self._create_many_assets(10, owner=self.test_stitcher_1)
        self._create_many_assets(5, owner=self.test_stitcher_2)

        count = 0
        for instance in MediaItem.objects.audios():
            self.assertIsInstance(instance.get_type_instance(), AudioAsset)
            count += 1

        self.assertEqual(count, 25)

    def test_media_item_queryset_videos(self):

        self._create_many_assets(10)
        self._create_many_assets(10, owner=self.test_stitcher_1)
        self._create_many_assets(5, owner=self.test_stitcher_2)

        count = 0
        for instance in MediaItem.objects.videos():
            self.assertIsInstance(instance.get_type_instance(), VideoAsset)
            count += 1

        self.assertEqual(count, 25)

    def test_media_item_queryset_documents(self):

        self._create_many_assets(10)
        self._create_many_assets(10, owner=self.test_stitcher_1)
        self._create_many_assets(5, owner=self.test_stitcher_2)

        count = 0
        for instance in MediaItem.objects.documents():
            self.assertIsInstance(instance.get_type_instance(), DocumentAsset)
            count += 1

        self.assertEqual(count, 25)

    def tearDown(self):

        # remove any test media
        if os.path.exists(self.test_media_root):
            try:
                shutil.rmtree(self.test_media_root)
            except Exception as e:
                print("Error in teardown [{}]".format(e))




