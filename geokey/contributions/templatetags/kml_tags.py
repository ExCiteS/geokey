from osgeo import ogr

from django import template

from geokey.categories.models import Field


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
    description = '<![CDATA[<table>'

    if properties:
        for key in properties:
            name = key

            try:
                field = Field.objects.get(
                    key=key,
                    category_id=place.get('meta').get('category').get('id')
                )
                name = field.name.encode('utf-8')
            except Field.DoesNotExist:
                pass

            value = properties[key]

            if type(value) in [str, unicode]:
                value = value.encode('utf-8')

            if properties[key] is not None:
                description = '{desc}<tr><td>{name}</td><td>{value}</td></tr>'.format(
                    desc=description,
                    name=name,
                    value=value
                )

    description = description + '</table>]]>'

    return description


@register.filter(name='kml_style')
def kml_style(place):
    colour = place.get('meta').get('category').get('colour')
    colour = colour.replace('#', '')
    return colour
