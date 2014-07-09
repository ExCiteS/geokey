from model_utils import Choices

LOCATION_STATUS = Choices('active', 'review')
OBSERVATION_STATUS = Choices(
    'active', 'draft', 'pending', 'deleted'
)
COMMENT_STATUS = Choices('active', 'deleted')
