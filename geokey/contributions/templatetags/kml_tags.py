"""Template tags for KML."""

from osgeo import ogr

from django import template

from geokey.categories.models import Field, LookupField, MultipleLookupField


register = template.Library()


@register.filter(name='kml_geom')
def kml_geom(place):
    geometry = place.get('location').get('geometry')
    json_geom = ogr.CreateGeometryFromJson(str(geometry))
    kml_geom = json_geom.ExportToKML()
    return kml_geom


@register.filter(name='kml_name')
def kml_name(place):
    name = ''  # Name will always be available, even it's empty

    if place:
        display_field = place.get('display_field')

        if display_field:
            name = display_field.get('value')

    return name


@register.filter(name='kml_desc')
def kml_desc(place):
    properties = place.get('properties')
    media = place.get('media')
    comments = place.get('comments')

    description = '<![CDATA['

    if properties:
        description += '<table>'

        for key in properties:
            name = key
            value = properties[key]

            try:
                field = Field.objects.get(
                    key=key,
                    category_id=place.get('meta').get('category').get('id')
                )
                name = field.name.encode('utf-8')

                if value is not None:
                    if isinstance(field, LookupField):
                        value = field.lookupvalues.get(pk=value).name
                    elif isinstance(field, MultipleLookupField):
                        values = field.lookupvalues.filter(
                            pk__in=value
                        )
                        value = '<br />'.join([v.name for v in values])
            except Field.DoesNotExist:
                pass

            if type(value) in [str, unicode]:
                value = value.encode('utf-8')

            if properties[key] is not None:
                description = '{desc}<tr><td>{name}</td><td>{value}</td></tr>'.format(
                    desc=description,
                    name=name,
                    value=value
                )

        description += '</table>'

    if media:
        description += '<table>'

        for file in media:
            if file['file_type'] == 'ImageFile' or file['file_type'] == 'VideoFile':
                if file['file_type'] == 'VideoFile':
                    file['url'] = file['url'].replace('embed/', 'watch?v=')

                description += '<tr><td><strong>{name}</strong>{desc}<br /><a href="{url}"><img src="{thumbnail_url}" /></a></td></tr>'.format(
                    name=file['name'],
                    desc='<br />%s' % file['description'] if file['description'] else '',
                    url=file['url'],
                    thumbnail_url=file['thumbnail_url']
                )
            elif file['file_type'] == 'AudioFile':
                description += '<tr><td><a href="{url}"><strong>{name}</strong></a>{desc}</td></tr>'.format(
                    name=file['name'],
                    desc='<br />%s' % file['description'] if file['description'] else '',
                    url=file['url']
                )

        description += '</table>'

    if comments:
        def render_comments(comments):
            description = '<table>'

            for comment in comments:
                description += '<tr><td><strong>{name}</strong>{text}'.format(
                    name=comment['creator']['display_name'],
                    text='<br />%s' % comment['text'] if comment['text'] else ''
                )

                if len(comment['responses']) > 0:
                    description += render_comments(comment['responses'])

                description += '</td></tr>'

            description += '</table>'

            return description

        description += render_comments(comments)

    description += ']]>'

    return description


@register.filter(name='kml_style')
def kml_style(place):
    colour = place.get('meta').get('category').get('colour')
    colour = colour.replace('#', '')
    return colour
