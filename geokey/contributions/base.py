"""Base for contributions."""

from model_utils import Choices


LOCATION_STATUS = Choices('active', 'review')
OBSERVATION_STATUS = Choices('active', 'draft', 'review', 'pending', 'deleted')
COMMENT_STATUS = Choices('active', 'deleted')
COMMENT_REVIEW = Choices('open', 'resolved')
MEDIA_STATUS = Choices('active', 'deleted')

ACCEPTED_IMAGE_FORMATS = ('png', 'jpeg', 'gif')
ACCEPTED_AUDIO_FORMATS = ('wav', 'wave', 'mp3', 'mpeg', '3gpp', '3gpp2')
ACCEPTED_VIDEO_FORMATS = (
    'mpeg', 'mpeg2', 'mp4', 'quicktime', '3gpp', '3gpp2', 'avi', 'x-flv',
    'x-matroska', 'x-msvideo', 'x-ms-wmv', 'ogg', 'webm'
)
