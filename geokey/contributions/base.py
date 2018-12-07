"""Base for contributions."""

from model_utils import Choices


LOCATION_STATUS = Choices('active', 'review')
OBSERVATION_STATUS = Choices('active', 'draft', 'review', 'pending', 'deleted')
COMMENT_STATUS = Choices('active', 'deleted')
COMMENT_REVIEW = Choices('open', 'resolved')
MEDIA_STATUS = Choices('active', 'deleted')

ACCEPTED_IMAGE_FORMATS = ('png', 'jpeg', 'gif')
ACCEPTED_AUDIO_FORMATS = (
    'wave', 'wav', 'x-wav', 'mp3', '3gpp', '3gpp2', 'mpeg', 'x-m4a', 'ogg',
    'amr', 'aiff', 'x-aiff'
)
ACCEPTED_FILE_TYPES = (
    # Audio types
    ('MPEG ADTS, layer III', 'mp3'),
    ('Ogg data, Opus audio', 'opus'),
    ('Ogg data, Vorbis audio', 'ogg'),
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
    ('OpenDocument Text', 'odt'),
    ('OpenDocument Spreadsheet', 'ods'),
    ('PDF document', 'pdf'),
    ('Composite Document File', 'doc'),
    ('XML', 'xml'),
    ('Microsoft OOXML', 'docx'),
    ('Microsoft Excel 2007+', 'xlsx'),
    ('Composite Document File', 'ppt'),
    ('Microsoft PowerPoint 2007+', 'pptx'),
    ('HTML document, ASCII text, with very long lines', 'xsl'),
    ('HTML document, ASCII text, with very long lines', 'xslt'),
)
ACCEPTED_VIDEO_FORMATS = (
    'mpeg', 'mpeg2', 'mp4', 'quicktime', '3gpp', '3gpp2', 'avi', 'x-flv',
    'x-matroska', 'x-msvideo', 'x-ms-wmv', 'ogg', 'webm'
)
ACCEPTED_DOCUMENT_FORMATS = ('pdf')
