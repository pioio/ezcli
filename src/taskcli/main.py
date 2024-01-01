"""Entrypoint for the 'taskcli' command."""


from dataclasses import dataclass
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

from .types import Module

log = get_logger(__name__)

def main() -> None:
    """Entrypoint for taskfiles that are meant to be ran via `./mytasks.py` or `python mytasks.py` .

    Note that you typically should invoke tasks via `t`, `tt`, `taskcli` commands.

    Example:
    ```
        from taskfile import tt, task, run

        @task
        def foobar():
            print("Hello!")
            run("ls -la")
i
        if __name__ == "__main__":
            tt.main()
    ```
    """
    module = sys.modules["__main__"]
    main_internal(done=True, from_module=module)

def _assert_taskcli_is_installed() -> None:
    try:
        import taskcli
    except ImportError as e:
        err = f"'taskcli' prackage is not installed, please install it with 'pip install taskcli: {e}'"
        utils.print_error(err)
        sys.exit(1)

def _debug_environment(from_module:Module|None=None):
    log.debug("Note: you can use -v, -vv, -vvv to show more verbose log output. "
              "See troubleshooting docs in case of problems.")
    log.debug("Current working directory: " + os.getcwd())
    log.debug(f"{sys.argv=}")
    if from_module:
        log.debug(f"main: {from_module=} {id(from_module)=}")

# @dataclass
# class Profiler:
#     import_took:float

# @dataclass
# class StartupContext:


def main_internal(done:bool=False, from_module:Module|None=None) -> None: # noqa: C901
    """Entrypoint for the `taskcli`, `tt`, and `t` commands.

    If you're calling from a script, use `main()` instead.
    """
    start = time.time()
    INVALID_TIME = -1.0

    log.separator("Starting main_internal()")
    _assert_taskcli_is_installed()
    _debug_environment(from_module=from_module)

    parser = build_initial_parser()

    from taskcli import tt

    argv = sys.argv[1:]
    argconfig, _ = parser.parse_known_args(argv)

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

        if parents:
            return parents[0]
        else:
            return ""

    for path in filepaths_to_include:
        assert os.path.exists(path), f"File not found: {path}"

    def include_from_filepaths(filepaths_to_include:list[str]) -> list[Task]:
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




def _find_default_file_in_dirs(default_files:list[str], dirs:list[str], ignore:list[str]|None=None) -> list[str]:
    out:list[str] = []

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

