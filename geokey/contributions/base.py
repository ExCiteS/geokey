"""Base for contributions."""

from model_utils import Choices


LOCATION_STATUS = Choices('active', 'review')
OBSERVATION_STATUS = Choices('active', 'draft', 'review', 'pending', 'deleted')
COMMENT_STATUS = Choices('active', 'deleted')
COMMENT_REVIEW = Choices('open', 'resolved')
MEDIA_STATUS = Choices('active', 'deleted')

ACCEPTED_FILE_TYPES = (
    # Audio types
    ('MPEG ADTS, layer III', 'mp3'),
    ('Audio file', 'mp3'),
    ('Ogg data', 'opus'),
    ('Ogg data', 'ogg'),
    ('WAVE audio', 'wav'),
    ('ALAC/AAC-LC (.M4A) Audio', 'm4a'),
    ('Adaptive Multi-Rate Codec', 'amr'),
    ('MPEG v4 system, 3GPP', '3gp'),
    ('AIFF audio', 'aiff'),
    ('MPEG ADTS, AAC', 'aac'),
    ('FLAC audio bitstream data', 'flac'),
    ('Microsoft ASF', 'wma'),
    ('Standard MIDI data', 'mid'),

    # Video types
    ('Apple QuickTime movie', 'mov'),
    ('RIFF (little-endian) data, AVI', 'avi'),
    ('Macromedia Flash Video', 'flv'),
    ('Matroska data', 'mkv'),
    ('MPEG sequence', 'mpg'),
    ('Macromedia Flash data', 'swf'),
    ('WebM', 'webm'),
    ('Microsoft ASF', 'wmv'),

    # Image types
    ('GIF image data', 'gif'),
    ('JPEG image data', 'jpg'),
    ('PNG image data', 'png'),

    # Office/document types
    ('PDF document', 'pdf'),
)
