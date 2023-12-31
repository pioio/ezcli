"""Entrypoint for the 'taskcli' command."""


import importlib.util
import os
import random
import string
import sys
import time
from typing import Callable

import taskcli.include

from . import envvars, taskfiledev, utils
from .logging import get_logger
from .parser import build_initial_parser
from .task import Task, UserError
from .utils import print_error, print_to_stderr

log = get_logger(__name__)


def main() -> None:  # noqa: C901
    """Entrypoint for the 'taskcli' command."""
    start = time.time()
    INVALID_TIME = -1.0

    try:
        import taskcli
    except ImportError:
        print("'taskcli' is not installed, please install it with 'pip install taskcli'")  # noqa: T201
        sys.exit(1)

    parser = build_initial_parser()
    argv = sys.argv[1:]
    argconfig, _ = parser.parse_known_args(argv or sys.argv[1:])

    tasks_found = False
    import_took = INVALID_TIME
    include_took = INVALID_TIME

    already_loaded = set()

    def include_from_file(
        filename: str,
        name_namespace: str = "",
        alias_namespace: str = "",
        mark_them: bool = False,
        filter: Callable[[Task], bool] | None = None,
    ) -> None:
        log.separator(f"Importing objects from {filename}")
        log.debug("Current working dir: " + os.getcwd())
        absolute_filepath = os.path.abspath(filename)
        log.debug(f"Absolute filepath: {absolute_filepath}")

        dir = os.path.dirname(absolute_filepath)
        sys.path.append(dir)
        # import module by name
        basename = os.path.basename(absolute_filepath)
        start_import = time.time()

        module_name = basename.replace(".py", "").replace("-", "_")
        log.debug(f"Importing module: {module_name}")
        #with utils.change_dir(dir):
        #print(os.getcwd(), module_name)
        imported_module = __import__(module_name)
        #print(os.getcwd(), "done", module_name)

        nonlocal import_took
        import_took = time.time() - start_import

        log.separator(f"Including tasks from {filename}")
        already_loaded.add(filename)

        start_include = time.time()  # FIXME: called for extra includes

        # This includes the tasks from 'sometasks' into THIS module (main)

        tasks = taskcli.include.include(
            imported_module,
            skip_include_info=True,
            name_namespace=name_namespace,
            alias_namespace=alias_namespace,
            filter=filter,
        )

        # TODO: fixme, this is needed for sortin those tasks to top. but right now they get duplicated
        # >>> for task in tasks:
        # >>>     task.from_above = True
        if mark_them:
            for task in tasks:
                task.name_format = f">{task.name_format}"
                blue = "\033[34m"
                task.name_format = blue + "⬆ {green}{name}{clear}"

        nonlocal include_took, tasks_found
        include_took = time.time() - start_include
        tasks_found = True

    for filename in argconfig.file.split(","):
        filename = filename.strip()
        if os.path.exists(filename):
            include_from_file(filename)
        else:
            print_error(f"File not found: {filename}")
            sys.exit(1)

    from taskcli import tt

    if tasks_found and tt.config.include_extra_tasks or not tasks_found:
        for filename in envvars.TASKCLI_EXTRA_TASKS_PY_FILENAMES.value.split(","):
            filename = filename.strip()
            if os.path.exists(filename):
                random_lowercase = "".join(random.choices(string.ascii_lowercase, k=8))

                random_lowercase = "taskcli_import_" + random_lowercase
                abs_filepath = os.path.abspath(filename)
                dir_filepath = os.path.dirname(abs_filepath)
                import shutil

                log.debug(f"Copying {abs_filepath} to {dir_filepath}/{random_lowercase}.py")
                target_filepath = f"{dir_filepath}/{random_lowercase}.py"
                try:
                    shutil.copy(abs_filepath, target_filepath)

                    if not tasks_found:  # not local tasks.py, it's not merging, so no namespace
                        include_from_file(target_filepath, mark_them=False)
                    else:
                        # might have
                        filterfun = tt.config.extra_tasks_filter
                        alias_namespace: str = tt.config.extra_tasks_alias_namespace
                        name_namespace: str = tt.config.extra_tasks_name_namespace
                        # By default no

                        include_from_file(
                            target_filepath,
                            name_namespace=name_namespace,
                            alias_namespace=alias_namespace,
                            mark_them=True,
                            filter=filterfun,
                        )
                finally:
                    try:
                        log.debug(f"Done! Now removing {target_filepath}.")
                        os.remove(f"{dir_filepath}/{random_lowercase}.py")
                    except UserError as e:
                        msg = f"Failed to remove temporary file {target_filepath}: {e}"
                        raise Exception(msg) from e

                log.debug("Done!")
                break  # for now only ones

    log.separator("Finished include and imports")
    # This part be right after importing the default ./task.p and before anything else
    # this way we allow ./tasks.py to change the default config, which in turn
    # might impact the output of get_argv()   (the default argument)
    argv = get_argv()

    this_module = sys.modules[__name__]
    taskfile_took = INVALID_TIME

    if taskfiledev.should_include_taskfile_dev(argv=argv):
        log.separator("Initializing go-task")
        start_taskfile = time.time()
        tasks_were_included = taskfiledev.include_tasks(to_module=this_module)
        if tasks_were_included:
            tasks_found = True
        taskfile_took = time.time() - start_taskfile

    dispatch_took = INVALID_TIME
    try:
        start_dispatch = time.time()
        log.separator("Dispatching tasks")
        taskcli.dispatch(argv=argv, tasks_found=tasks_found)
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


def get_argv() -> list[str]:
    """Return the command line arguments. Prefixed with default options if needed.

    There's a different set of default options for 't|taskcli' and 'tt' commands
    """
    from taskcli import tt

    if utils.is_basename_tt():
        # when calling with "tt"

        # Let's always add --show-hidden - more consistent behavior to users who forget to specify it
        # when customizing options.
        builtin_tt_options = ["--show-hidden"]
        argv = ["--show-hidden"] + tt.config.default_options_tt + sys.argv[1:]
        if tt.config.default_options_tt:
            log.debug(
                f"Using custom default options (tt): {tt.config.default_options_tt}, "
                f"plus the built-in options: {builtin_tt_options}"
            )
    else:
        # when calling with "t" or "taskcli"
        argv = tt.config.default_options + sys.argv[1:]
        if tt.config.default_options:
            log.debug(f"Using custom default options (taskcli): {tt.config.default_options}")
    return argv
