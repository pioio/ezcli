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

    ready = False
    for filename in envvars.TASKCLI_TASKS_PY_FILENAMES.value.split(","):
        filename = filename.strip()
        if os.path.exists(filename):
            sys.path.append(os.getcwd())

            # import module by name
            tasks = __import__(filename.replace(".py", ""))

            taskcli.include(tasks)
            ready = True

    if taskfiledev.should_include_taskfile_dev():
        tasks_were_included = taskfiledev.include_tasks()
        if tasks_were_included:
            ready = True

    if ready:
        taskcli.dispatch()
        return
    else:
        # TODO, check upper dirs
        print(  # noqa: T201
            "taskcli: No tasks file found in current directory, "
            f"looked for: {envvars.TASKCLI_TASKS_PY_FILENAMES.value}. "
            f"Set the environment variable {envvars.TASKCLI_TASKS_PY_FILENAMES.name} to a comma separated "
            "list of filename to change the "
            "list of filenames to look for. See docs for details."
        )
        local_taskfile = taskfiledev.has_taskfile_dev()

        if taskfiledev.has_taskfile_dev() and not taskfiledev.should_include_taskfile_dev():
            print(  # noqa: T201
                f"taskcli: Note: found a {local_taskfile} file. "
                "See the docs on how to include and list its tasks automatically."
            )
        sys.exit(1)
