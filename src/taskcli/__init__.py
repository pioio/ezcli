import logging

log = logging.getLogger(__name__)
log.debug("Initializing taskcli")

from .taskcli import argument
from .taskcli import group
from .taskcli import option
#from .taskcli import usage
from .taskcli import SETTINGS

