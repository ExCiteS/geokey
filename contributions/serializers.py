import json
import requests
import tempfile
from django.core import files

from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import PermissionDenied
from django.utils.html import strip_tags

from easy_thumbnails.files import get_thumbnailer

from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers

from rest_framework.serializers import BaseSerializer
from rest_framework_gis.serializers import GeoFeatureModelListSerializer

from core.exceptions import MalformedRequestData
from categories.serializer import CategorySerializer
from categories.models import Category
from users.serializers import UserSerializer

from .models.contributions import Observation, Comment
from .models.locations import Location
from .models.media import MediaFile, ImageFile, VideoFile


class LocationSerializer(geoserializers.GeoFeatureModelSerializer):
    class Meta:
        model = Location
        geo_field = 'geometry'
        fields = ('id', 'name', 'description', 'status', 'created_at')
        write_only_fields = ('status',)


class LocationContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        depth = 1
        fields = ('id', 'name', 'description', 'status', 'created_at')
        write_only_fields = ('status',)


class ContributionSerializer(BaseSerializer):
    class Meta:
        list_serializer_class = GeoFeatureModelListSerializer

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        kwargs['context']['many'] = True
        return GeoFeatureModelListSerializer(*args, **kwargs)

    def validate_category(self, project, category_id):
        errors = []
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

    def is_valid(self, raise_exception=False):
        project = self.context.get('project')
        meta = self.initial_data.get('meta')

        self._errors = {}
        self._validated_data = self.initial_data

        if self.instance is None and meta is not None:
            self.validate_category(project, meta.get('category'))

        if self._errors and raise_exception:
            raise MalformedRequestData(self._errors)

        return not bool(self._errors)

    def create(self, validated_data):
        project = self.context.get('project')
        meta = validated_data.pop('meta')

        location = self.restore_location(
            data=validated_data.pop('location', None),
            geometry=validated_data.get('geometry')
        )

        self.instance = Observation.create(
            properties=validated_data.get('properties'),
            creator=self.context.get('user'),
            location=location,
            project=project,
            category=meta.get('category'),
            status=meta.pop('status', None)
        )

        return self.instance

    def update(self, instance, validated_data):
        meta = validated_data.get('meta')
        status = None
        if meta is not None:
            status = meta.get('status', None)

        self.restore_location(
            instance.location,
            data=validated_data.pop('location', None),
            geometry=validated_data.pop('geometry', None)
        )

        return instance.update(
            properties=validated_data.get('properties'),
            updator=self.context.get('user'),
            status=status
        )

    def restore_location(self, instance=None, data=None, geometry=None):
        if instance is not None:
            if data is not None:
                instance.name = data.get('name') or instance.name
                instance.description = (data.get('description') or
                                        instance.description)
                private = data.get('private') or instance.private
                private_for_project = (data.get('private_for_project') or
                                       instance.private_for_project)

            if geometry is not None:
                if type(geometry) is not unicode:
                    geometry = json.dumps(geometry)

                instance.geometry = GEOSGeometry(geometry)

            instance.save()
            return instance
        else:
            if (data is not None) and ('id' in data):
                try:
                    return Location.objects.get_single(
                        self.context.get('user'),
                        self.context.get('project').id,
                        data.get('id')
                    )
                except PermissionDenied, error:
                    raise MalformedRequestData(error)
            else:
                name = None
                description = None
                private_for_project = None
                private = False

                if data is not None:
                    name = strip_tags(data.get('name'))
                    description = strip_tags(data.get('description'))
                    private = data.get('private')
                    private_for_project = data.get('private_for_project')

                return Location(
                    name=name,
                    description=description,
                    geometry=GEOSGeometry(json.dumps(geometry)),
                    private=private,
                    private_for_project=private_for_project,
                    creator=self.context.get('user')
                )

    def get_display_field(self, obj):
        if obj.display_field is not None:
            display_field = obj.display_field.split(':', 1)
            value = display_field[1] if display_field[1] != 'None' else None
            return {
                'key': display_field[0],
                'value': value
            }
        else:
            return None

    def get_search_result(self, obj, q):
        search_matches = {}

        matcher = obj.search_matches.split('#####')

        for field in matcher:
            match = field.split(':', 1)
            if q.lower() in match[1].lower():
                search_matches[match[0]] = match[1]

        return search_matches

    def to_representation(self, obj):
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
            'type': 'Feature',
            'geometry': json.loads(location.geometry.geojson),
            'properties': obj.properties,
            'meta': {
                'status': obj.status,
                'creator': {
                    'id': obj.creator.id,
                    'display_name': obj.creator.display_name
                },
                'updator': (updator),
                'created_at': obj.created_at,
                'version': obj.version,
                'isowner': isowner
            },
            'location': {
                'id': location.id,
                'name': location.name,
                'description': location.description
            }
        }

        if self.context.get('many'):
            category_serializer = CategorySerializer(
                obj.category,
                context=self.context,
                fields=('id', 'name', 'description', 'symbol', 'colour')
            )
            feature['meta']['category'] = category_serializer.data

            feature['display_field'] = self.get_display_field(obj)

            q = self.context.get('search')
            if q is not None:
                feature['search_matches'] = self.get_search_result(obj, q)
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
    creator = UserSerializer(fields=('id', 'display_name'))
    isowner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'respondsto', 'created_at', 'text', 'isowner',
                  'creator', 'review_status')
        read_only = ('id', 'respondsto', 'created_at')

    def to_representation(self, obj):
        native = super(CommentSerializer, self).to_representation(obj)
        native['responses'] = CommentSerializer(
            obj.responses.all(),
            many=True,
            context=self.context
        ).data

        return native

    def get_isowner(self, comment):
        if not self.context.get('user').is_anonymous():
            return comment.creator == self.context.get('user')
        else:
            return False


class FileSerializer(serializers.ModelSerializer):
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
        """
        return obj.type_name

    def get_isowner(self, obj):
        """
        Returns `True` if the user provided in the serializer context is the
        creator of this file
        """
        if not self.context.get('user').is_anonymous():
            return obj.creator == self.context.get('user')
        else:
            return False

    def get_url(self, obj):
        """
        Return the url to access this file based on its file type
        """
        if isinstance(obj, ImageFile):
            return obj.image.url
        elif isinstance(obj, VideoFile):
            return obj.youtube_link

    def _get_thumb(self, image, size=(300, 300)):
        thumbnailer = get_thumbnailer(image)
        thumb = thumbnailer.get_thumbnail({
            'crop': True,
            'size': size
        })
        return thumb

    def get_thumbnail_url(self, obj):
        """
        Creates and returns a thumbnail for the ImageFile object
        """
        if isinstance(obj, ImageFile):
            return self._get_thumb(obj.image).url

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
