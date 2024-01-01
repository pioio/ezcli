import time

from . import logging

log = logging.get_logger(__name__)


class Timer:
    """Simple timer context manager that logs how long it took to run the code inside it."""

    def __init__(self, name: str):
        self.name = name
        self.start = time.time()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.end = time.time()
        self.took = self.end - self.start
        log.debug(f"{self.name} took {self.took:.3f}s")
