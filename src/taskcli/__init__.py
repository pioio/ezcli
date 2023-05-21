import logging

log = logging.getLogger(__name__)
log.debug("Initializing taskcli")

from .taskcli import task, cli, arg#, analyze_signature
