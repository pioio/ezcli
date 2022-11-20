import logging


log = logging.getLogger(__name__)


def task(func):
    def wrapper():
        log.debug("Before task decorator")
        func()
        log.debug("After decorator")

    return wrapper


def somefunction():
    log.info("core - some function")
