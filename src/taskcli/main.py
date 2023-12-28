"""Entrypoint for the 'taskcli' command."""

import json
import logging
import os
import sys

from . import envvars, task, taskfiledev
from .parser import build_initial_parser
from .utils import print_err, print_error
import time

log = logging.getLogger(__name__)


def main() -> None:
    """Entrypoint for the 'taskcli' command."""
    start = time.time()

    try:
        import taskcli
    except ImportError:
        print("'taskcli' module is not installed, please install it with 'pip install taskcli'")  # noqa: T201
        sys.exit(1)

    parser = build_initial_parser()
    argv = sys.argv[1:]
    argconfig, _ = parser.parse_known_args(argv or sys.argv[1:])

    tasks_found = False
    import_took = 999
    include_took = 999
    for filename in argconfig.file.split(","):
        filename = filename.strip()
        if os.path.exists(filename):
            dir = os.path.dirname(filename)
            sys.path.append(dir)
            # import module by name
            basename = os.path.basename(filename)
            start_import = time.time()
            sometasks = __import__(basename.replace(".py", "").replace("-", "_"))
            import_took = time.time() - start_import

            log.debug(f"Including tasks from {filename}")
            start_include = time.time()
            taskcli.include(sometasks)
            include_took = time.time() - start_include
            tasks_found = True

    if taskfiledev.should_include_taskfile_dev():
        tasks_were_included = taskfiledev.include_tasks()
        if tasks_were_included:
            tasks_found = True

    dispatch_took = 999
    try:
        start_dispatch = time.time()
        taskcli.dispatch(tasks_found=tasks_found)
        dispatch_took = time.time() - start_dispatch
    finally:
        if envvars.TASKCLI_ADV_PRINT_RUNTIME.is_true():
            took = time.time() - start
            print(f"Runtime: {took:.3f}s")
            print(f"    Import: {import_took:.3f}s")
            print(f"   Include: {include_took:.3f}s")
            print(f"  Dispatch: {include_took:.3f}s")