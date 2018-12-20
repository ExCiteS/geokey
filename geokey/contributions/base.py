"""Base for contributions."""

from model_utils import Choices


LOCATION_STATUS = Choices('active', 'review')
OBSERVATION_STATUS = Choices('active', 'draft', 'review', 'pending', 'deleted')
COMMENT_STATUS = Choices('active', 'deleted')
COMMENT_REVIEW = Choices('open', 'resolved')
MEDIA_STATUS = Choices('active', 'deleted')
ACCEPTED_AUDIO_TYPES = (
    ('MPEG ADTS, layer III', 'mp3'),
    ('Audio file', 'mp3'),
    ('Ogg data, Opus audio', 'opus'),
    ('Ogg data', 'ogg'),
    ('WAVE audio', 'wav'),
    ('AAC-LC (.M4A) Audio', 'm4a'),
    ('MPEG v4 system', 'm4a'),
    ('Adaptive Multi-Rate Codec', 'amr'),
    ('MPEG v4 system, 3GPP', '3gp'),
    ('AIFF audio', 'aiff'),
    ('AAC', 'aac'),
    ('FLAC audio bitstream data', 'flac'),
    ('Microsoft ASF', 'wma'),
)
ACCEPTED_VIDEO_TYPES = (
    ('Apple QuickTime movie', 'mov'),
    ('RIFF (little-endian) data, AVI', 'avi'),
    ('Macromedia Flash Video', 'flv'),
    ('Matroska data', 'mkv'),
    ('MPEG sequence', 'mpg'),
    ('Macromedia Flash data', 'swf'),
    ('WebM', 'webm'),
    ('Microsoft ASF', 'wmv'),
)
ACCEPTED_IMAGE_TYPES = (
    ('GIF image data', 'gif'),
    ('JPEG image data', 'jpg'),
    ('PNG image data', 'png'),
    ('Scalable Vector Graphics', 'svg'),
    ('TIFF image data', 'tiff'),
)
ACCEPTED_DOC_TYPES = (
    ('PDF document', 'pdf'),
)
ACCEPTED_FILE_TYPES = \
    ACCEPTED_AUDIO_TYPES + \
    ACCEPTED_VIDEO_TYPES + \
    ACCEPTED_IMAGE_TYPES + \
    ACCEPTED_DOC_TYPES
