import json
from rest_framework.parsers import BaseParser


class GeoJsonParser(BaseParser):
    """Parses GeoJson into deserialisable native Python objects """
    media_type = 'application/json'

    def parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}

        request_data = stream.read()
        data = json.loads(request_data)

        parsed = {}

        if 'id' in data:
            parsed['id'] = data.pop('id')

        if 'location' in data:
            parsed['location'] = data.pop('location')

        if 'properties' in data:
            parsed['properties'] = data.pop('properties')

        if 'geometry' in data:
            if 'location' not in parsed:
                parsed['location'] = {}

            parsed['location']['geometry'] = json.dumps(data.pop('geometry'))

        if 'meta' in data:
            parsed.update(data.pop('meta'))

        return parsed
