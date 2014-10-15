from django.db import models
from django.conf import settings

class MediaFile(models.Model):
    """
    Base class for all media files. Not to be instaciate; instaciate one of
    the child classes instead.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    contribution = models.ForeignKey(
        'contributions.Observation', related_name='files_attached'
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'contributions'

    @property
    def type_name(self):
        """
        Returns the type of media file. To be implemented by child classes.
        """
        raise NotImplementedError(
            'The property `type_name` has not been implemented for this '
            'subclass of `MediaFile`.'
        )


class ImageFile(MediaFile):
    """
    Stores images uploaded by users.
    """
    image = models.ImageField(upload_to='user-uploads')

    class Meta:
        app_label = 'contributions'

    @property
    def type_name(self):
        """
        Returns 'ImageFile'
        """
        return 'ImageFile'
