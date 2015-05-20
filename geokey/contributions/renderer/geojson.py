import json
from rest_framework.renderers import BaseRenderer


class GeoJsonRenderer(BaseRenderer):
    """
    Renderes serialised Contributions into GeoJson
    """
    media_type = 'application/json'
    format = 'json'

    def render_single(self, data):
        data['geometry'] = data.get('location').pop('geometry')
        return data

    def render_many(self, data):
        return {
            "type": "FeatureCollection",
            "features": [self.render_single(item) for item in data]
        }

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized GeoJson.
        """
        if data is None:
            return ''

        if isinstance(data, dict):
            rendered = self.render_single(data)
        else:
            rendered = self.render_many(data)

        return json.dumps(rendered)
