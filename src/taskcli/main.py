"""Entrypoint for the 'taskcli' command."""

import json
import logging
import os
import sys

from . import envvars, task, taskfiledev
from .parser import build_initial_parser
from .utils import print_err, print_error

log = logging.getLogger(__name__)


def main() -> None:
    """Entrypoint for the 'taskcli' command."""
    from taskcli import dispatch

    try:
        import taskcli
    except ImportError:
        print("'taskcli' module is not installed, please install it with 'pip install taskcli'")  # noqa: T201
        sys.exit(1)

    parser = build_initial_parser()
    argv = sys.argv[1:]
    argconfig, _ = parser.parse_known_args(argv or sys.argv[1:])

    tasks_found = False
    for filename in argconfig.file.split(","):
        filename = filename.strip()
        if os.path.exists(filename):
            dir = os.path.dirname(filename)
            sys.path.append(dir)
            # import module by name
            basename = os.path.basename(filename)
            sometasks = __import__(basename.replace(".py", "").replace("-", "_"))

            log.debug(f"Including tasks from {filename}")
            taskcli.include(sometasks)
            tasks_found = True

    if taskfiledev.should_include_taskfile_dev():
        tasks_were_included = taskfiledev.include_tasks()
        if tasks_were_included:
            tasks_found = True

    taskcli.dispatch(tasks_found=tasks_found)
