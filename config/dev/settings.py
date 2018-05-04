import os
from who_the_hill import utils

DEBUG=True
TEMPLATE_PATH = '%s/who_the_hill/templates/' % os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

LOG = utils.setup_logging()