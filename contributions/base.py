from model_utils import Choices

LOCATION_STATUS = Choices('active', 'review')
OBSERVATION_STATUS = Choices(
    'active', 'draft', 'review', 'pending', 'suspended', 'deleted'
)
COMMENT_STATUS = Choices('active', 'deleted')
