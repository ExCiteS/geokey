"""GeoJSON parser."""

import json
from rest_framework.parsers import BaseParser


class GeoJsonParser(BaseParser):
    """Parses GeoJson into deserialisable native Python objects """
    media_type = 'application/json'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the GeoJson imput and returns deserialisable Python native
        """
        parser_context = parser_context or {}

        request_data = stream.read()
        data = json.loads(request_data)

        if 'geometry' in data:
            if 'location' not in data:
                data['location'] = {}

            data['location']['geometry'] = json.dumps(data.pop('geometry'))

        return data
