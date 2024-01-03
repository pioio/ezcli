"""Main entrypoint for executing `taskcli` Tasks.

In a nutshell, the code here does the following
- basic early CLI parsing (e.g. -f)
- locate the main and the parent taskfiles,
- import and include tasks from them.

Much more details in comments further below.
"""
import argparse
from ast import arg
from genericpath import isdir
from logging import root
import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from taskcli import init

import taskcli.include
from .modulesettings import get_module_settings
from . import envvars, taskfiledev, utils
from .logging import get_logger
from .task import Task
from .timer import Timer
from .types import Module, UserError
from .utils import print_error

log = get_logger(__name__)


def main() -> None:
    """Entrypoint for taskfiles that were ran via `./tasks.py` or `python tasks.py` .

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
    """Entrypoint for the `taskcli`, `tt`, and `t` commands.

    Declared via pyproject.toml.
    """
    with Timer("Grand total"):
        try:
            _main_internal(module_with_imported_tasks=from_module)
        except UserError as e:
            # This is a type of error we want to handle gracefully, and sypress the stacktrace of.
            from taskcli import tt
            if tt.config.verbose:
                log.exception(e)
            utils.print_error(f"{e}  (use -v to show the stacktrace)")
            sys.exit(1)

    from .timer import summary
    for k, v in summary.items():
        log.debug(f"{v}: {k}")


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

    We always look for the main file, and optionally for the parent file.
    We always first look for the main task file, and include before looking for the parent, because
    the main task file might contain settings that impact the parent task file.

    In this function we don't abort if we fail to locate any tasks. This happens only later on.
    """
    from taskcli import tt
    with _section("Init of init"):
        log.separator("Starting main_internal()")
        _assert_taskcli_is_installed()
        _debug_environment(from_module=module_with_imported_tasks)
        early_config: _EarlyConfig = _init_early_config()
        init_stats = tt.get_runtime().init_stats

    ################################################################################################################
    with _section("Initialization"):
        root_module, TASKS_ALREADY_INCLUDED = _determine_root_module(module_with_imported_tasks)
        del module_with_imported_tasks
        if TASKS_ALREADY_INCLUDED:
            init_stats.inspected_files.append(root_module.__file__ or "(unknown filename)")

    if TASKS_ALREADY_INCLUDED:
        # No need to search for, or load, any files.
        # The tasks (if any) have been imported and included to this module already.
        # We just need to load them into the runtime.
        # This will happen later
        pass
    else:
        # The if/else branch attemps to import the tasks and include them into THIS module.

        # Allow to specify many files, include from many
        main_taskfiles_path: str = ""

        ################################################################################################################
        with _section("Searching for the main taskfile"):
            # The 'main taskfile' is either specified with -f, is in the current dir, or a few dirs up
            main_taskfiles_path = _locate_main_taskfile(early_config, default_files=envvars.TASKCLI_TASKS_PY_FILENAMES.value.split(","))

            # it's OK if none were found.

            init_stats.inspected_files.extend(main_taskfiles_path)

        ################################################################################################################
        if main_taskfiles_path:
            with _section("Importing and including the main taskfile"):
                # This function does Python import of the tasks.
                # The import also initializes `tt.config`` with any custom settings defined in the tasks.py
                #  - this might impact whether or not we should look for the parent further down
                # After this initial include, it's safe to use tt.config.
                _import_and_include_main_taskfile(main_taskfiles_path)

        ################################################################################################################
        parent_taskfile_path:str = ""

        with _section("Searching for the parent taskfile"):
            from taskcli import tt
            if not main_taskfiles_path:
                log.debug("Skipping, no main taskfile was found")
            else:

                main_module = sys.modules[os.path.abspath(main_taskfiles_path)]
                module_settings = get_module_settings(main_module)

                INCLUSION_OF_PARENT_TASKFILE_WAS_REQUESTED = early_config.parent or tt.config.parent or module_settings.include_parent

                if not INCLUSION_OF_PARENT_TASKFILE_WAS_REQUESTED:
                    log.debug("No parent taskfile was requested by the user, not looking for it")
                    parent_taskfile_path = ""
                else:
                    log.debug(f"Parent taskfile was request via {early_config.parent=} or/and "
                              f"{tt.config.parent=} or/and {module_settings.include_parent=}")
                    assert main_taskfiles_path
                    main_taskfile_path = main_taskfiles_path if main_taskfiles_path else ""
                    parent_taskfile_path = _find_parent_taskfile_path(
                        early_config,
                        paths_to_ignore=[main_taskfiles_path],
                        start_path=main_taskfile_path
                      )

        ################################################################################################################
        if parent_taskfile_path:
            main_module = sys.modules[os.path.abspath(main_taskfiles_path)]
            module_settings = get_module_settings(main_module)
            with _section("Importing and including the parent taskfile"):
                _include_parent_taskfile(parent_taskfile_path, filter=module_settings.parent_task_filter)
            init_stats.inspected_files.extend(parent_taskfile_path)
            init_stats.parent_taskfile_path = parent_taskfile_path


        ################################################################################################################
        if taskfiledev.should_include_taskfile_dev(sys.argv):
            with _section("Importing and including third-party taskfile (yaml from the taskfile.dev project)"):
                search_in_dir = main_taskfiles_path if main_taskfiles_path else "."
                if taskfiledev.include_tasks(to_module=root_module, path=search_in_dir):
                    init_stats.inspected_files.extend(
                        f"[Output of the {envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.value} binary]")


    ####################################################################################################################
    with _section("Include/Import finished, now running dispatch()"):
        taskcli.dispatching.dispatch(argv=sys.argv[1:], module=root_module)

    log.debug("Finished main_internal()")


########################################################################################################################
# Private classes
@dataclass
class _EarlyConfig:
    """Typesafe wrapper of the argpase.Namespace object using during the initial start."""

    parent: str
    file: str


########################################################################################################################
# Less-important private helper functions

def _find_and_include_go_task_taskfile(to_module:Module, path:str):
    taskfiledev.include_tasks(to_module=to_module, path=path)


def _determine_root_module(module_with_imported_tasks:Module|None) -> tuple[Module, bool]:
        """Determine the module containing the tasks.

        If the tasks were already imported, return the module containing them (it was provided).
        Otherwise, return the module containing this function.

        Thus, this function MUST remain in main.py (uses sys.modules[__name__])
        """
        if module_with_imported_tasks:
            root_module = module_with_imported_tasks
            TASKS_ALREADY_INCLUDED = True
        else:
            TASKS_ALREADY_INCLUDED = False
            root_module = sys.modules[__name__]

        log.debug(f"Root module containing the tasks: {root_module=}, {id(root_module)=}, {TASKS_ALREADY_INCLUDED=}")
        return root_module, TASKS_ALREADY_INCLUDED

@contextmanager
def _section(name: str):
    """Start a section with a timer. Logs will have runtime of the section, and a separator line will be printed."""
    with Timer(name):
        log.separator(name)
        yield
        log.debug("---")




def _init_early_config(argv: list[str] | None = None) -> _EarlyConfig:
    """Create a temporary config objects that wrap around the results of initial parsing."""
    argv = argv or sys.argv[1:]
    parser = _build_initial_parser()
    argconfig, _ = parser.parse_known_args(argv)

    if "_ARGCOMPLETE" in os.environ and "COMP_LINE" in os.environ:
        # This is needed for tab completion whtn -p or -f are specified, otherwise e.g. doing '-f ../tasks.py'
        # would show complete from local tasks.py

        compline = os.environ["COMP_LINE"]
        # FIXME: This won't work well if theres args with spaces in them, but should be good enough for most cases.
        args = compline.split(" ")
        argconfig, _ = parser.parse_known_args(args)



    return _EarlyConfig(file=argconfig.file, parent=argconfig.parent)


def _import_and_include_main_taskfile(filepath_to_include: str) -> list[Task]:
    from taskcli import tt
    log.debug(f"main: {filepath_to_include=}")
    included: list[Task] = []
    filepath = filepath_to_include

    filepath = filepath.strip()
    absolute_filepath = os.path.abspath(filepath)
    if os.path.exists(absolute_filepath):
        # TODO: rename to "preserve groups?"


        # tt.include(str) imports the python modules
        included.extend(tt.include(filepath, skip_include_info=True))
    else:
        msg = f"File not found: {filepath}"
        raise UserError(msg)

    return included


def _include_parent_taskfile(parent_path: str,filter) -> None:
    """Includes a specified taskfile, and marks all tasks from it as obtained "from parent".

    This marking can later be used for filtering or formatting
    """
    from taskcli import tt

    log.debug(f"main: {parent_path=}")
    tasks_from_parent = tt.include(parent_path, skip_include_info=True, filter=filter, name_namespace_if_conflict="p")
    for task in tasks_from_parent:
        task.group.from_parent = True
        task.from_parent = True


def _locate_main_taskfile(early_config: _EarlyConfig, default_files: list[str]) -> str:
    out = ""
    if early_config.file:
        log.debug(f"main: -f was specified: {early_config.file=}")
        for path in early_config.file.split(","):
            # for path in early_config.file:
            abspath = os.path.abspath(path)
            if not os.path.exists(path):
                if path != abspath:
                    msg = f"Specified file not found: {path} (absolute path is {abspath})"
                else: # path == abspath
                    msg = f"Specified file not found: {path}"
                raise UserError(msg)

            if os.path.isdir(abspath):
                res = _find_default_file_in_dirs(default_files=default_files, dirs=[abspath])
                if res:
                    out = res[0]
            else:
                out = abspath
    else:
        log.debug(
            f"main: '-f <filename>' was not specified explicitly; looking for default files to include. {os.getcwd()=}"
        )
        log.debug("  The candidate default files to include are: " + str(default_files))
        log.debug("  Will try to include the first one encountered.")
        dirs_to_check = ["./", "../", "../../", "../../../", "../../../../", "../../../../../"]
        log.debug("  Will now look for them in the following dirs: " + str(dirs_to_check))

        res = _find_default_file_in_dirs(default_files=default_files, dirs=dirs_to_check)
        if res:
            out = res[0]
    if not out:
        log.debug("No taskfiles found")
    return out


def _find_parent_taskfile_path(early_config: _EarlyConfig, start_path:str, paths_to_ignore: list[str]) -> str:
    """Return the first found parent taskfile.

    Search relative to start_path, not to user's CWD.
    """
    with utils.change_dir(os.path.dirname(start_path)):
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
        raise UserError(err) from e


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
    """Return a list of absolute filepaths to any default taskfiles found in the specified dirs."""
    out: list[str] = []

    log.debug(f"{ignore=}")
    found = False
    for dir in dirs:
        if not os.path.isdir(dir):
            msg = f"Not a directory: {dir}"
            raise UserError(msg)

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

    for out_path in out:
        assert os.path.isabs(out_path)
    #print (f"Found default files: {out}")
    return out
