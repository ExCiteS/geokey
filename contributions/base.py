from model_utils import Choices

LOCATION_STATUS = Choices('active', 'review')
OBSERVATION_STATUS = Choices(
    'active', 'draft', 'pending', 'deleted'
)
COMMENT_STATUS = Choices('active', 'deleted')

ACCEPTED_IMAGE_FORMATS = ('png', 'jpeg', 'gif')
ACCEPTED_VIDEO_FORMATS = ('mpeg', 'mp4', 'quicktime', 'x-msvideo', '3gpp',
                          'x-flv', 'x-ms-wmv')
