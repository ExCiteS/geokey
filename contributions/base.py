from model_utils import Choices

LOCATION_STATUS = Choices('active', 'review')
OBSERVATION_STATUS = Choices(
    'active', 'draft', 'pending', 'deleted'
)
COMMENT_STATUS = Choices('active', 'deleted')

ACCEPTED_IMAGE_FORMATS = ('.png', '.jpeg', '.jpg', '.gif')
ACCEPTED_VIDEO_FORMATS = ('.mov', '.mpeg4', '.avi', '.wmv', '.flv', '.3gpp',
                          '.webm', '.mp4', '.mpegps')
