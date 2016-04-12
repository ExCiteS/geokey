"""Serializers for contributions."""

import requests
import tempfile

from django.core import files
from django.core.exceptions import PermissionDenied, ValidationError

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError

from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers

from rest_framework.serializers import BaseSerializer

from geokey.categories.serializers import CategorySerializer
from geokey.categories.models import Category
from geokey.users.serializers import UserSerializer

from .models import (
    Observation,
    Location,
    Comment,
    MediaFile,
    ImageFile,
    VideoFile,
    AudioFile
)


class LocationSerializer(geoserializers.GeoFeatureModelSerializer):
    """
    Serialiser for geokey.contribtions.models.Location
    """
    class Meta:
        model = Location
        geo_field = 'geometry'
        fields = ('id', 'name', 'description', 'status', 'created_at')
        write_only_fields = ('status',)


class LocationContributionSerializer(serializers.ModelSerializer):
    """
    Serialiser for `Location`; to be used within `ContributionSerializer`.
    """
    class Meta:
        model = Location
        fields = ('id', 'name', 'description', 'status', 'created_at',
                  'geometry', 'private', 'private_for_project')
        write_only_fields = ('status', 'private', 'private_for_project')

    def create(self, validated_data):
        """
        Creates a new contribution from `validated_data`

        Parameter
        ---------
        validated_data : dict
            Input data after validation

        Returns
        -------
        Location
        """
        validated_data['creator'] = self.context.get('user')
        return super(
            LocationContributionSerializer,
            self
        ).create(validated_data)


class ContributionSerializer(BaseSerializer):
    """
    Serialiser for geokey.contribtions.models.Observations. This is a custom
    serialiser, not a standard ModelSerializer
    """
    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        Is called when many=True property is set when instantiating the
        serialiser.
        """
        kwargs['context']['many'] = True
        return super(ContributionSerializer, cls).many_init(*args, **kwargs)

    def validate_category(self, project, category_id):
        """
        Validates if the category can be used with the project

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that the category is used for
        category_id : int
            identifies the category in the database

        Returns
        -------
        geokey.categories.models.Category
            The valid category
        """
        errors = []
        category = None
        try:
            category = project.categories.get(pk=category_id)
            if category.status == 'inactive':
                errors.append('The category can not be used because it is '
                              'inactive.')
            else:
                self._validated_data['meta']['category'] = category
        except Category.DoesNotExist:
            errors.append('The category can not be used with the project '
                          'or does not exist.')

        if errors:
            self._errors['category'] = errors

        return category

    def replace_null(self, properties):
        """
        Replaces all empty str or unicode values with None and returns the
        properies dict

        Parameter
        ---------
        properties : dict
            Contribution properties

        Returns
        -------
        dict
            Contribution properties with replaced null values

        """
        for key, value in properties.iteritems():
            if isinstance(value, (str, unicode)) and len(value) == 0:
                properties[key] = None

        return properties

    def validate_properties(self, properties, category=None, status=None):
        """
        Validates the properties and adds error messages to self._errors

        Parameter
        ---------
        properties : dict
            Contribution properties
        category : geokey.categories.models.Category
            Category the properties are validated against
        status : str
            Status for the contribution
        """
        errors = []

        if self.instance:
            status = status or self.instance.status
            if self.instance.properties:
                update = self.instance.properties.copy()
                update.update(properties)
                properties = update
        else:
            status = status or category.default_status

        properties = self.replace_null(properties)
        try:
            if status == 'draft':
                Observation.validate_partial(category, properties)
            else:
                Observation.validate_full(category, properties)
        except ValidationError, e:
            errors.append(e)

        self._validated_data['properties'] = properties
        self._validated_data['meta']['status'] = status

        if errors:
            self._errors['properties'] = errors

    def validate_location(self, project, location_id):
        """
        Validates if the location can be used with the project

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that the category is used for
        location_id : int
            identifies the location in the database
        """
        errors = []
        self.location = None

        try:
            if location_id is not None:
                self.location = Location.objects.get_single(
                    self.context.get('user'),
                    project.id,
                    location_id
                )
        except PermissionDenied, error:
            errors.append(error)
        except Location.DoesNotExist, error:
            errors.append(error)

        if errors:
            self._errors['location'] = errors

    def is_valid(self, raise_exception=False):
        """
        Checks if the contribution that is deserialised is valid. Validates
        location, category and properties.

        Parameter
        ---------
        raise_exception : Boolean
            indicates if an exeption should be raised if the data is invalid.
            If set to false, this method will return False if the data is
            invalid.

        Returns
        -------
        Boolean
            indicating if data is valid

        Raises
        ------
        ValidationError
            If data is invalid. Exception is raised when raise_exception is set
            tp True.
        """
        self._errors = {}
        self._validated_data = self.initial_data

        project = self.context.get('project')
        meta = self.initial_data.get('meta')

        if meta is None:
            self._validated_data['meta'] = dict()

        # Validate location
        location_id = None
        if self.initial_data.get('location') is not None:
            location_id = self.initial_data.get('location').get('id')
        self.validate_location(project, location_id)

        # Validate category
        category = None
        if self.instance is None and meta is not None:
            category = self.validate_category(project, meta.get('category'))
        else:
            category = self.instance.category
        self._validated_data['meta']['category'] = category

        # Validatie properties
        properties = self.initial_data.get('properties') or {}
        status = None
        if meta is not None:
            status = meta.get('status', None)
        if properties is not None and category is not None:
            self.validate_properties(
                properties,
                category=category,
                status=status
            )

        # raise the exception
        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)

    def create(self, validated_data):
        """
        Creates a new observation and returns the instance.

        Parameter
        ---------
        validated_data : dict
            the data dict after validation

        Returns
        -------
        geokey.contributions.models.Observation
            The instance created
        """
        project = self.context.get('project')
        meta = validated_data.pop('meta')

        location_serializer = LocationContributionSerializer(
            self.location,
            data=validated_data.pop('location', None),
            context=self.context
        )
        if location_serializer.is_valid():
            location_serializer.save()

        self.instance = Observation.create(
            properties=validated_data.get('properties'),
            creator=self.context.get('user'),
            location=location_serializer.instance,
            project=project,
            category=meta.get('category'),
            status=meta.pop('status', None)
        )

        return self.instance

    def update(self, instance, validated_data):
        """
        Updates an existing observation and returns the instance.

        Parameter
        ---------
        instance : geokey.contributions.models.Observation
            the instance to be updated
        validated_data : dict
            the data dict after validation

        Returns
        -------
        geokey.contributions.models.Observation
            The instance update
        """
        meta = validated_data.get('meta')
        status = None
        if meta is not None:
            status = meta.get('status', None)

        location_serializer = LocationContributionSerializer(
            instance.location,
            data=validated_data.pop('location', {}),
            context=self.context,
            partial=True
        )
        if location_serializer.is_valid():
            location_serializer.save()

        return instance.update(
            properties=validated_data.get('properties'),
            updator=self.context.get('user'),
            status=status
        )

    def get_display_field(self, obj):
        """
        Returns a native representation of the display_field property.

        Parameter
        ---------
        obj : geokey.contributions.models.Observation
            The instance that is serialised

        Returns
        -------
        dict
            serialised display_field; e.g.
            {
                'key': 'field_key',
                'value': 'The value of the field'
            }
        """
        if obj.display_field is not None:
            display_field = obj.display_field.split(':', 1)
            value = display_field[1] if display_field[1] != 'None' else None
            return {
                'key': display_field[0],
                'value': value
            }
        else:
            return None

    def to_representation(self, obj):
        """
        Returns the native representation of a contribution

        Parameter
        ---------
        obj : geokey.contributions.models.Observation
            The instance that is serialised

        Returns
        -------
        dict
            Native represenation of the Contribution
        """
        location = obj.location

        isowner = False
        if not self.context.get('user').is_anonymous():
            isowner = obj.creator == self.context.get('user')

        updator = None
        if obj.updator is not None:
            updator = {
                'id': obj.updator.id,
                'display_name': obj.updator.display_name
            }

        feature = {
            'id': obj.id,
            'properties': obj.properties,
            'display_field': self.get_display_field(obj),
            'meta': {
                'status': obj.status,
                'creator': {
                    'id': obj.creator.id,
                    'display_name': obj.creator.display_name
                },
                'updator': updator,
                'created_at': str(obj.created_at),
                'updated_at': str(obj.updated_at),
                'version': obj.version,
                'isowner': isowner,
                'num_media': obj.num_media,
                'num_comments': obj.num_comments
            },
            'location': {
                'id': location.id,
                'name': location.name,
                'description': location.description,
                'geometry': location.geometry.geojson
            }
        }

        if self.context.get('many'):
            cat = obj.category
            feature['meta']['category'] = {
                'id': cat.id,
                'name': cat.name,
                'description': cat.description,
                'symbol': cat.symbol.url if cat.symbol else None,
                'colour': cat.colour
            }

        else:
            category_serializer = CategorySerializer(
                obj.category, context=self.context)
            feature['meta']['category'] = category_serializer.data

            comment_serializer = CommentSerializer(
                obj.comments.filter(respondsto=None),
                many=True,
                context=self.context
            )
            feature['comments'] = comment_serializer.data

            review_serializer = CommentSerializer(
                obj.comments.filter(review_status='open'),
                many=True,
                context=self.context
            )
            feature['review_comments'] = review_serializer.data

            file_serializer = FileSerializer(
                obj.files_attached.all(),
                many=True,
                context=self.context
            )
            feature['media'] = file_serializer.data

        return feature


class CommentSerializer(serializers.ModelSerializer):
    """
    Serialiser for geokey.contributions.models.Comment
    """
    creator = UserSerializer(fields=('id', 'display_name'), read_only=True)
    isowner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'respondsto', 'created_at', 'text', 'isowner',
                  'creator', 'review_status')
        read_only = ('id', 'respondsto', 'created_at')

    def to_representation(self, obj):
        """
        Returns native represenation of the Comment. Adds responses to comment

        Parameter
        ---------
        obj : geokey.contributions.models.Comment
            The instance that is serialised

        Returns
        -------
        dict
            Native represenation of the Comment

        """
        native = super(CommentSerializer, self).to_representation(obj)
        native['responses'] = CommentSerializer(
            obj.responses.all(),
            many=True,
            context=self.context
        ).data

        return native

    def get_isowner(self, comment):
        """
        Returns True if the user serialising the Comment has created the
        comment

        Parameter
        ---------
        comment : geokey.contributions.models.Comment
            The instance that is serialised

        Returns
        -------
        Boolean
            indicating of user is creator of comment
        """
        if not self.context.get('user').is_anonymous():
            return comment.creator == self.context.get('user')
        else:
            return False


class FileSerializer(serializers.ModelSerializer):
    """
    Serialiser for geokey.contributions.models.MediaFile instances
    """
    creator = UserSerializer(fields=('id', 'display_name'))
    isowner = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = (
            'id', 'name', 'description', 'created_at', 'creator', 'isowner',
            'url', 'thumbnail_url', 'file_type'
        )

    def get_file_type(self, obj):
        """
        Returns the type of the MediaFile

        Parameter
        ---------
        obj : geokey.contributions.models.MediaFile
            The instance that is serialised

        Returns
        -------
        str
            The type of the, e.g. 'ImageFile'
        """
        return obj.type_name

    def get_isowner(self, obj):
        """
        Returns `True` if the user provided in the serializer context is the
        creator of this file

        Parameter
        ---------
        obj : geokey.contributions.models.MediaFile
            The instance that is serialised

        Returns
        -------
        Boolean
            indicating if user created the file
        """
        if not self.context.get('user').is_anonymous():
            return obj.creator == self.context.get('user')
        else:
            return False

    def get_url(self, obj):
        """
        Return the url to access this file based on its file type

        Parameter
        ---------
        obj : geokey.contributions.models.MediaFile
            The instance that is serialised

        Returns
        -------
        str
            The URL to embed the file on client side
        """
        if isinstance(obj, ImageFile):
            return obj.image.url
        elif isinstance(obj, VideoFile):
            return obj.youtube_link
        elif isinstance(obj, AudioFile):
            return obj.audio.url

    def _get_thumb(self, image, size=(300, 300)):
        """
        Returns the thumbnail of the media file base on the size privoded

        Parameter
        ---------
        image : Image
            The image to be thumbnailed
        size : tuple
            width and height of the thumbnail, defaults to 300 by 300

        Returns
        -------
        Image
            The thumbnail

        """
        thumbnailer = get_thumbnailer(image)
        thumb = thumbnailer.get_thumbnail({
            'crop': True,
            'size': size
        })
        return thumb

    def get_thumbnail_url(self, obj):
        """
        Creates and returns a thumbnail for the MediaFile object

        Parameter
        ---------
        obj : geokey.contributions.models.MediaFile
            The instance that is serialised

        Returns
        -------
        str
            The url to embed thumbnails on client side
        """
        if isinstance(obj, ImageFile):
            # Some of the imported image files in the original community maps
            # seem to be broken. The error thrown when the image can not be
            # read is caught here.
            try:
                return self._get_thumb(obj.image).url
            except (
                IOError,
                InvalidImageFormatError
            ):
                return ''

        elif isinstance(obj, VideoFile):
            if obj.thumbnail:
                # thumbnail has been downloaded, return the link
                return self._get_thumb(obj.thumbnail).url

            request = requests.get(
                'http://img.youtube.com/vi/%s/0.jpg' % obj.youtube_id,
                stream=True
            )

            if request.status_code != requests.codes.ok:
                # Image not found, return placeholder thumbnail
                return '/static/img/play.png'

            lf = tempfile.NamedTemporaryFile()
            # Read the streamed image in sections
            for block in request.iter_content(1024 * 8):

                # If no more file then stop
                if not block:
                    break

                # Write image block to temporary file
                lf.write(block)

            file_name = obj.youtube_id + '.jpg'
            obj.thumbnail.save(file_name, files.File(lf))

            from PIL import Image

            w, h = Image.open(obj.thumbnail).size

            thumb = self._get_thumb(obj.thumbnail, size=(h, h))
            obj.thumbnail.save(file_name, thumb)

            return self._get_thumb(obj.thumbnail).url

        elif isinstance(obj, AudioFile):
            return '/static/img/play.png'
