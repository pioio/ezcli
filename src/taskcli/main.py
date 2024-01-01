"""Entrypoint for the 'taskcli' command."""


import os
import sys
import time

from requests import get

import taskcli.include

from . import envvars, taskfiledev, utils
from .logging import get_logger
from .parser import build_initial_parser
from .task import Task, UserError
from .utils import print_error, print_to_stderr
from taskcli import task, tt
from .types import Module

log = get_logger(__name__)

def main() -> None:
    """Call this from your tasks.py if you want to be able to run it via './tasks.py' directly."""
    module = sys.modules["__main__"]
    main_internal(done=True, from_module=module)


def main_internal(done:bool=False, from_module:Module|None=None) -> None: # noqa: C901
    """Entrypoint for the 'taskcli' command."""
    start = time.time()
    INVALID_TIME = -1.0

    log.separator("Starting main")
    if from_module:
        log.debug(f"main: {from_module=} {id(from_module)=}")

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

    # allow to specify many files, include from many
    filepaths_to_include:list[str] = []
    default_files =  envvars.TASKCLI_TASKS_PY_FILENAMES.value.split(",")

    if not done:
        # If file, or files, were explicitly specified, they must exist
        if argconfig.file:
            log.debug(f"main: -f was specified: {argconfig.file=}")
            for path in argconfig.file.split(","):
                abspath = os.path.abspath(path)
                if not os.path.exists(path):
                    print_error(f"Specified file not found: {path} (absolute: {abspath})")
                    sys.exit(1)
                filepaths_to_include.append(abspath)
        else:
            log.debug(f"main: '-f <filename>' was not specified explicitly; looking for default files to include. {os.getcwd()=}")
            log.debug("  The candidate default files to include are: " + str(default_files))
            log.debug("  Will try to include the first one encountered.")
            dirs_to_check = ["./", "../", "../../", "../../../", "../../../../", "../../../../../"]
            log.debug("  Will now look for them in the following dirs: " + str(dirs_to_check))


            filepaths_to_include.extend(_find_default_file_in_dirs(default_files=default_files, dirs=dirs_to_check))

    def get_parent_path() -> str:
        log.debug(f"main: -p was specified: {argconfig.parent=}")
        dirs_to_check = ["../", "../../", "../../../", "../../../../", "../../../../../"]
        parents = _find_default_file_in_dirs(default_files=default_files, dirs=dirs_to_check, ignore=filepaths_to_include)
        log.debug("Found parents: " + str(parents))
        #return parents[0]
        if parents:
            return parents[0]
        else:
            return ""

    #if not done and (argconfig.parent or tt.config.parent):
    for path in filepaths_to_include:
        assert os.path.exists(path), f"File not found: {path}"

    def include_from_filepaths(filepaths_to_include:list[str]) -> list[Task]:
        # if not filepaths_to_include:
        #     cwd = os.getcwd()
        #     msg = f"taskcli: No files to include in '{cwd}'. Run 'taskcli --init' to create a new 'tasks.py', or specify one with -f ."
        #     print_to_stderr(msg, color="")
        #     sys.exit(1)
        for filepath in filepaths_to_include:
            filepath = filepath.strip()
            absolute_filepath = os.path.abspath(filepath)
            if os.path.exists(absolute_filepath):
                # TODO: rename to "preserve groups?"
                return tt.include(filepath, skip_include_info=True)
            else:
                print_error(f"File not found: {filepath}")
                sys.exit(1)
        return []

    if not done:
        log.separator("Initial include")
        log.debug(f"Initial include: {filepaths_to_include=}")

        # This does Python import, initializing tt.config with settings defined in the tasks.py
        # so, after this initial include, it's safe to use tt.config in this function
        include_from_filepaths(filepaths_to_include)

        if argconfig.parent or tt.config.parent:
            log.debug(f"main: parent was specified: via {argconfig.parent=} or {tt.config.parent=}")
            if parent_path := get_parent_path():
                log.debug(f"Parent include: {filepaths_to_include=}")
                log.debug(f"main: {parent_path=}")
                tasks_from_parent = tt.include(parent_path, skip_include_info=True)
                for task in tasks_from_parent:
                    task.group.from_parent = True
                    task.from_parent = True



    log.separator("Finished include and imports")


    taskfile_took = INVALID_TIME

    dispatch_took = INVALID_TIME
    try:
        start_dispatch = time.time()
        log.separator("Dispatching tasks")

        if from_module is None:
            from_module = sys.modules[__name__]

        log.debug(f"About to call dispatch, , {from_module=} {id(from_module)=}")
        taskcli.dispatch(argv=argv, module=from_module)
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

LS = list[str]

def _find_default_file_in_dirs(default_files:LS, dirs:LS, ignore:LS|None=None) -> LS:
    out:LS = []

    log.debug(f"{ignore=}")
    found = False
    for dir in dirs:
        if found:
            break
        for path in default_files:
            if not os.path.isabs(path):
                path = os.path.join(dir, path)

            path = path.strip()
            log.debug(f"  Checking if {path=} exists")
            if os.path.exists(path):
                abspath = os.path.abspath(path)
                if ignore and abspath in ignore:
                    log.debug(f"  Ignoring {abspath=} because its in the ignore list: {ignore=}")
                    continue

                log.debug(f"  Found default file: {path=}  (absolute path is {abspath}), not searching further")
                out.append(abspath)
                found= True
                break
    return out


def _get_parent_path(path:str) -> str:
    """Return the parent dir of the given path."""
    return os.path.abspath(os.path.join(path, os.pardir))