import logging

log = logging.getLogger(__name__)
log.debug("Initializing taskcli")

from .taskcli import cli
from .core import task
from .core import flavor
from .core import Task
