"""Entrypoint for the 'taskcli' command."""

import json
import logging
import os
import sys
import time

from . import envvars, task, taskfiledev, utils
from .parser import build_initial_parser
from .utils import print_err, print_error

log = logging.getLogger(__name__)


def main() -> None:  # noqa: C901
    """Entrypoint for the 'taskcli' command."""
    start = time.time()
    INVALID_TIME = -1.0

    try:
        import taskcli
    except ImportError:
        print("'taskcli' module is not installed, please install it with 'pip install taskcli'")  # noqa: T201
        sys.exit(1)

    parser = build_initial_parser()
    argv = sys.argv[1:]
    argconfig, _ = parser.parse_known_args(argv or sys.argv[1:])

    tasks_found = False
    import_took = INVALID_TIME
    include_took = INVALID_TIME
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

    taskfile_took = INVALID_TIME
    if taskfiledev.should_include_taskfile_dev():
        start_taskfile = time.time()
        tasks_were_included = taskfiledev.include_tasks()
        if tasks_were_included:
            tasks_found = True
        taskfile_took = time.time() - start_taskfile

    dispatch_took = INVALID_TIME
    try:
        start_dispatch = time.time()
        taskcli.dispatch(tasks_found=tasks_found)
        dispatch_took = time.time() - start_dispatch
    finally:
        if envvars.TASKCLI_ADV_PRINT_RUNTIME.is_true():
            took = time.time() - start
            utils.print_stderr(f"Runtime: {took:.3f}s")
            if import_took != INVALID_TIME:
                utils.print_stderr(f"    Import: {import_took:.3f}s")

            if include_took != INVALID_TIME:
                utils.print_stderr(f"   Include: {include_took:.3f}s")

            if dispatch_took != INVALID_TIME:
                utils.print_stderr(f"  Dispatch: {dispatch_took:.3f}s")

            if taskfile_took != INVALID_TIME:
                utils.print_stderr(
                    f"  Taskfile: {taskfile_took:.3f}s (time to run the 'task' binary, "
                    f"{envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH})"
                )
