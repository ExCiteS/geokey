"""GeoJSON renderer."""

import json

from rest_framework.renderers import BaseRenderer


class GeoJsonRenderer(BaseRenderer):
    """
    Renderes serialised Contributions into GeoJson
    """
    media_type = 'application/json'
    format = 'json'
    separators = (',', ':')

    def render_single(self, data):
        """
        Renders a single `Contribution` into GeoJson
        """
        data['type'] = "Feature"
        data['geometry'] = json.loads(data.get('location').pop('geometry'))
        return data

    def render_many(self, data):
        """
        Creates a `FeatureCollection` object and adds Contributions to
        `features`.
        """
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

        if 'error' in data:
            rendered = data
        elif isinstance(data, dict):
            rendered = self.render_single(data)
        else:
            rendered = self.render_many(data)

        return json.dumps(rendered, separators=self.separators)
