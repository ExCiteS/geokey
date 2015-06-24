from django.template.loader import render_to_string

from rest_framework.renderers import BaseRenderer


class KmlRenderer(BaseRenderer):

    media_type = 'application/vnd.google-earth.kml+xml'
    format = 'kml'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return ''

        if 'error' in data:
            rendered = data
        else:
            rendered = render_to_string(
                'geometries/placemarks.kml',
                {'data': data}
            )

        return rendered
