import os

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


class FileValidatorFunction(object):
    """
    Define  class as validator so django migrations can pickle it.
    """

    def __init__(self, max_file_size=None, allowed_mimetypes=None, allowed_extensions=None):
        self.max_file_size = max_file_size
        self.allowed_mimetypes = allowed_mimetypes
        self.allowed_extensions = allowed_extensions

    def __call__(self, uploaded_file):
        try:
            import magic
        except ImportError:
            magic = None

        max_file_size, allowed_mimetypes, allowed_extensions = (
            self.max_file_size,
            self.allowed_mimetypes,
            self.allowed_extensions
        )

        if max_file_size is not None and uploaded_file.size > max_file_size:
            raise ValidationError(
                "File size of {} is larger than the max allowed size of {}".format(
                    filesizeformat(uploaded_file.size),
                    filesizeformat(max_file_size)
                )
            )

        if allowed_mimetypes:
            if magic:
                # Use python-magic wrapper over libmagic to extract mimetype from headers
                try:
                    mimetype = magic.from_buffer(uploaded_file.read(1024), mime=True)
                    if mimetype not in allowed_mimetypes:
                        raise ValidationError(
                            '{} is not a valid content type for this field'.format(
                                mimetype
                            )
                        )
                except ValidationError:
                    raise
                except Exception as e:
                    raise ValidationError(
                        'Unable to determine content type of uploaded file. [{}]'.format(
                            getattr(e, 'message', str(e))
                        )
                    )
            else:
                if uploaded_file.content_type.lower() not in allowed_mimetypes:
                    raise ValidationError(
                        '{} is not a valid content type for this field'.format(
                            uploaded_file.content_type
                        )
                    )

        if allowed_extensions:
            try:
                extension = os.path.splitext(uploaded_file.name)[-1]
                if extension.lower() not in allowed_extensions:
                    raise ValidationError(
                        '{} is not a valid file extension for this field'.format(
                            extension.lower()
                        )
                    )
            except ValidationError:
                raise
            except (AttributeError, IndexError) as e:
                raise ValidationError(
                    'Unable to determine file extension. [{}]'.format(
                        getattr(e, 'message', str(e))
                    )
                )

        return True

    def deconstruct(self):
        """To allow Django to serialise the validator"""

        return (
            'projects.models.FileValidatorFunction',
            [],
            {
                'max_file_size': self.max_file_size,
                'allowed_mimetypes': self.allowed_mimetypes,
                'allowed_extensions': self.allowed_extensions
            }
        )
