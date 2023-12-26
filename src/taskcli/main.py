"""Entrypoint for the 'taskcli' command."""

import json
import logging
import os
import sys

from . import envvars, taskfiledev

log = logging.getLogger(__name__)


def main() -> None:
    """Entrypoint for the 'taskcli' command."""
    from taskcli import dispatch

    try:
        import taskcli
    except ImportError:
        print("'taskcli' module is not installed, please install it with 'pip install taskcli'")  # noqa: T201
        sys.exit(1)

    taskcli.dispatch()
