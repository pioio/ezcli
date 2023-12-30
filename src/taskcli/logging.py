"""Configuration of the taskcli logger.

This module defines a custom logger which adds a 'trace' method.

Overall, the more `-v` flags are added to the command line (e.g. `-vvv`), the more
verbose the logging will be.

"""

import logging
from typing import Any


class Logger(logging.Logger):
    """Custom logger which adds a trace method."""

    def trace(self, msg: Any, level: int = 3, *args: Any, **kwargs: Any) -> None:
        """Log message to debug, but only if verbose level high enough.

        Args:
            msg: message to log
            level: how many -v flags were used:
                   2 = -vv, 3 = -vvv, etc.
            args: passed through to logging.debug()
            kwargs: passed through to logging.debug()
        """
        from . import tt

        if tt.config.verbose >= level:
            msg = "TRACE: " + msg
            self.debug(msg, *args, **kwargs)

    def separator(self, msg: str = "") -> None:
        """Print a separator line to the log."""
        green = "\033[92m"
        clear = "\033[0m"

        self.debug(f"{green}=====================[{msg}]========================{clear}")


def get_logger(name: str) -> Logger:
    """Return a logger with the specified name."""
    del name  # discard the name for now, always return the same logger.
    return _logger


_logger = Logger("taskcli")


def configure_logging() -> None:
    """Configure logging for taskcli.

    Should be called only once.
    """
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-v", "--verbose", action="count", default=0)
    import sys

    args, _ = parser.parse_known_args(sys.argv[1:])

    from . import tt

    tt.config.verbose = args.verbose  # hack: set it early, as otherwise all taskcliconfig args are read only later

    log = get_logger("")

    handler = logging.StreamHandler(sys.stderr)
    if args.verbose >= 1:
        log.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)

    # You can also format the handler output
    if args.verbose <= 1:
        formatter = logging.Formatter("%(asctime)s %(levelname)-7s|  %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s %(levelname)-7s|  %(message)-100s  [%(filename)s:%(lineno)d]")
    handler.setFormatter(formatter)

    # Add the handler to the logger
    log.handlers.clear()
    log.addHandler(handler)

    log.debug("Logging configured.")
    log.debug("Debug logging enabled.")
    log.trace("Trace logging enabled. Logs will be very verbose.")
