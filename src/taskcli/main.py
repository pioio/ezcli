"""Main entrypoint for executing tasks command.

Overview:
- do basic early CLI parsing,
- locate the main and the parent taskfiles,
- import and include tasks from them.

Much more details in comments further below.
"""
import argparse
import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field

import taskcli.include

from . import envvars, taskfiledev, utils
from .logging import get_logger
from .task import Task, UserError
from .timer import Timer
from .types import Module
from .utils import print_error

log = get_logger(__name__)


def main() -> None:
    """Entrypoint for taskfiles that are meant to be ran via `./tasks.py` or `python tasks.py` .

    Note that you typically should invoke tasks via `t`, `tt`, `taskcli` commands.

    Example:
    ```
        from taskfile import tt, task, run

        @task
        def foobar():
            print("Hello!")
            run("ls -la")

        if __name__ == "__main__":
            tt.main()
    ```
    """
    module = sys.modules["__main__"]
    main_internal(from_module=module)


def main_internal(from_module: Module | None = None) -> None:
    """Entrypoint for the `taskcli`, `tt`, and `t` commands."""
    with Timer(_main_internal.__name__):
        _main_internal(module_with_imported_tasks=from_module)


########################################################################################################################
# This is the main function of this module


def _main_internal(module_with_imported_tasks: Module | None = None) -> None:
    """Make sure the tasks have been loaded, and then call dispatch() for further exection.

    Args:
        module_with_imported_tasks: An optional python module containing already imported the tasks.

    In details:
      - Create a simple parser to parse the initial flags like "-f" and "-p"
      - Then, either:
          a) find, import, and include the main taskfiles (if invoke by `t|tt|taskfile`), or
          b) include already imported tasks from the `from_module` (if invoked by `./taskfile.py` or `python ...`)
      - Check if loading tasks from a parent taskfile was requested, and if so, find it, import it, and include them.
      - At this point all the tasks that will ever be needed have been both imported and included.
        - But they have not been loaded to the main runtime yet (happens later)
      - We call dispatch() to load the tasks and continue parsing the CLI to decide what to do (e.g. list or run them)

    We always look for the main file, and optionally for the parent file
    In this function we don't abort if we fail to locate any tasks. This happens only later on.
    """
    log.separator("Starting main_internal()")
    _assert_taskcli_is_installed()
    _debug_environment(from_module=module_with_imported_tasks)
    early_config: _EarlyConfig = _init_early_config()

    if module_with_imported_tasks:
        # No need to search for, or load any files.
        # The tasks (if any) have been imported and included to this module already.
        # We just need to load them into the runtime later
        pass
    else:
        # The branch attemps to import the tasks and include them into THIS module.

        # Allow to specify many files, include from many
        main_taskfiles_paths: list[str] = []

        ################################################################################################################
        with _section("Searching for the main taskfile"):
            # The 'main taskfile' is either specified with -f, is in the current dir, or a few dirs up
            main_taskfiles_paths.extend(
                _locate_main_taskfiles(
                    early_config, default_files=envvars.TASKCLI_TASKS_PY_FILENAMES.value.split(",")
                )
            )

        ################################################################################################################
        if main_taskfiles_paths:
            with _section("Importing and including the main taskfile"):
                # This function does Python import of the tasks.
                # The import also initializes `tt.config`` with any custom settings defined in the tasks.py
                #  - this might impact whether or not we should look for the parent further down
                # After this initial include, it's safe to use tt.config.
                _import_and_include_main_taskfile(main_taskfiles_paths)

        ################################################################################################################
        with _section("Searching for the parent taskfile"):
            from taskcli import tt
            INCLUSION_OF_PARENT_TASKFILE_WAS_REQUESTED = early_config.parent or tt.config.parent
            if not INCLUSION_OF_PARENT_TASKFILE_WAS_REQUESTED:
                log.debug("No parent taskfile was requested by the user, not looking for it")
                parent_path = ""
            else:
                log.debug(f"Parent taskfile was request via {early_config.parent=} or/and {tt.config.parent=}")
                parent_path = _get_parent_taskfile_path(early_config, paths_to_ignore=main_taskfiles_paths)

        ################################################################################################################
        if parent_path:
            with _section("Importing and including the parent taskfile"):
                _include_parent_taskfile(parent_path)

    ###################################################################################################################
    with _section("Finished importing and including Tasks, calling dispatch()"):
        module_with_imported_tasks = _determine_module_containing_the_tasks(from_module=module_with_imported_tasks)
        taskcli.dispatch(argv=sys.argv[1:], module=module_with_imported_tasks)

    log.debug("Finished main_internal()")

########################################################################################################################
# Private classes
@dataclass
class _EarlyConfig:
    """Typesafe wrapper of the argpase.Namespace object using during the initial start."""

    parent: str
    file: str


########################################################################################################################
# Private helper functions

@contextmanager
def _section(name: str):
    """Start a section with a timer. Logs will have runtime of the section, and a separator line will be printed."""
    with Timer(name):
        log.separator(name)
        yield
        log.debug("---")


def _determine_module_containing_the_tasks(from_module: Module | None = None) -> Module:
    """Return the module containing the tasks.

    If no module was specified by the call to main, we use THIS module.

    This means that the function doing the tt.include of the initial taskfile must also be in this module.
    """
    if from_module is None:
        from_module = sys.modules[__name__]
    return from_module


def _init_early_config(argv: list[str] | None = None) -> _EarlyConfig:
    """Create a temporary config objects that wrap around the results of initial parsing."""
    argv = argv or sys.argv[1:]
    parser = _build_initial_parser()
    argconfig, _ = parser.parse_known_args(argv)
    return _EarlyConfig(file=argconfig.file, parent=argconfig.parent)


def _import_and_include_main_taskfile(filepaths_to_include: list[str]) -> list[Task]:
    from taskcli import tt

    included: list[Task] = []
    for filepath in filepaths_to_include:
        filepath = filepath.strip()
        absolute_filepath = os.path.abspath(filepath)
        if os.path.exists(absolute_filepath):
            # TODO: rename to "preserve groups?"

            # tt.include(str) imports the python modules
            included.extend(tt.include(filepath, skip_include_info=True))
        else:
            print_error(f"File not found: {filepath}")
            sys.exit(1)
    return included


def _include_parent_taskfile(parent_path: str) -> None:
    """Includes a specified taskfile, and marks all tasks from it as obtained "from parent".

    This marking can later be used for filtering or formatting
    """
    from taskcli import tt

    log.debug(f"main: {parent_path=}")
    tasks_from_parent = tt.include(parent_path, skip_include_info=True)
    for task in tasks_from_parent:
        task.group.from_parent = True
        task.from_parent = True


def _locate_main_taskfiles(early_config: _EarlyConfig, default_files: list[str]) -> list[str]:
    out: list[str] = []
    if early_config.file:
        log.debug(f"main: -f was specified: {early_config.file=}")
        for path in early_config.file.split(","):
            # for path in early_config.file:
            abspath = os.path.abspath(path)
            if not os.path.exists(path):
                print_error(f"Specified file not found: {path} (absolute: {abspath})")
                sys.exit(1)
            out.append(abspath)
    else:
        log.debug(
            f"main: '-f <filename>' was not specified explicitly; looking for default files to include. {os.getcwd()=}"
        )
        log.debug("  The candidate default files to include are: " + str(default_files))
        log.debug("  Will try to include the first one encountered.")
        dirs_to_check = ["./", "../", "../../", "../../../", "../../../../", "../../../../../"]
        log.debug("  Will now look for them in the following dirs: " + str(dirs_to_check))

        out.extend(_find_default_file_in_dirs(default_files=default_files, dirs=dirs_to_check))
    if not out:
        log.debug("No taskfiles found")
    return out


def _get_parent_taskfile_path(early_config: _EarlyConfig, paths_to_ignore: list[str]) -> str:
    """Return the first found parent taskfile."""
    default_files = envvars.TASKCLI_TASKS_PY_FILENAMES.value.split(",")
    log.debug(f"main: -p was specified: {early_config.parent=}")
    dirs_to_check = ["../", "../../", "../../../", "../../../../", "../../../../../"]
    parents = _find_default_file_in_dirs(default_files=default_files, dirs=dirs_to_check, ignore=paths_to_ignore)

    out = ""
    if parents:
        out = parents[0]
        log.debug(f"Found parent taskfiles: {parents}, returning {out}")
    else:
        log.debug("No parent taskfiles found")

    if parents:
        return parents[0]
    else:
        return ""


def _assert_taskcli_is_installed() -> None:
    try:
        import taskcli
    except ImportError as e:
        err = f"'taskcli' prackage is not installed, please install it with 'pip install taskcli: {e}'"
        utils.print_error(err)
        sys.exit(1)


def _debug_environment(from_module: Module | None = None):
    """Print various debug info about the environment."""
    log.debug(
        "Note that you can use -vv and -vvv to show even more verbose log output. "
        "See the 'troubleshooting' docs page for more info."
    )

    log.debug("Current working directory: " + os.getcwd())

    log.debug(f"{sys.argv=}")

    if from_module:
        log.debug(f"main: {from_module=} {id(from_module)=}")

    envvars.print_set_taskcli_env_vars(log.debug)


def _build_initial_parser() -> argparse.ArgumentParser:
    """Build small parser containing only the flags needed early in the execution.

    This is needed to parse flags like "-f" to load the initial taskfile.
    After that is done, later on, the full parser is constructed
    """
    root_parser = argparse.ArgumentParser(add_help=False)

    from taskcli import tt

    config = tt.config
    config.configure_early_parser(root_parser)
    return root_parser


def _find_default_file_in_dirs(default_files: list[str], dirs: list[str], ignore: list[str] | None = None) -> list[str]:
    out: list[str] = []

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
                found = True
                break
    return out
