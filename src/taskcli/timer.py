import time

from . import logging

log = logging.get_logger(__name__)

summary:dict[str,str] = {}

_indent = 0
class Timer:
    """Simple timer context manager that logs how long it took to run the code inside it."""

    def __init__(self, name: str):

        self.name = name

        self.start = time.time()

    def __enter__(self):
        global _indent
        _indent += 1
        indent_txt = "  " * _indent
        summary[self.name] = f"{indent_txt}entered"
        return self

    def __exit__(self, *exc):
        global _indent
        indent_txt = "  " * _indent
        self.end = time.time()
        self.took = self.end - self.start
        log.debug(f"{self.name} took {self.took:.3f}s")
        summary[self.name] = f"{indent_txt}{self.took:.3f}s"
        _indent -= 1
