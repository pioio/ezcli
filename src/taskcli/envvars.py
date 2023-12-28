"""Environment variables used by taskcli."""
import logging
import os
import sys

from taskcli import configuration

from .envvar import EnvVar

log = logging.getLogger(__name__)

TASKCLI_TASKS_PY_FILENAMES = EnvVar(
    default_value="tasks.py",
    desc="Comma separated list of filenames which 'taskcli' tool should include by default.",
)

TASKCLI_GOTASK_TASK_BINARY_FILEPATH = EnvVar(
    default_value="",
    desc=(
        "The absolute path to the binary of the taskfile.dev tool. Used to include tasks from Taskfile.yaml files."
        "Setting this can add 20ms to each execution of taskcli if taskfile yaml files are in the local directory."
    ),
)

TASKCLI_GOTASK_TASKFILE_FILENAMES = EnvVar(
    default_value="Taskfile.yaml,Taskfile.yml,taskfile.yaml,taskfile.yml",
    desc=(
        "Comman separated list of Taskfiles.dev filenames form which to include tasks. "
        "TASKCLI_GOTASK_TASK_BINARY_FILEPATH must be set for this to work."
    ),
)

TASKCLI_GOTASK_TASK_NAME_PREFIX = EnvVar(
    default_value="tf:", desc=("String to prefix to all task names from a Taskfile.dev yaml file. ")
)

TASKCLI_GOTASK_TASK_GROUP_NAME = EnvVar(
    default_value="Taskfile.dev", desc=("Name of the group to which tasks from 'task' binary should be added.")
)

# Various advanced settings. You typically don't need to change these.
TASKCLI_ADV_OVERRIDE_FORMATTING = EnvVar(
    default_value="false",
    desc=(
        "If set to true, overrides formatting options to make the listing output simpler. "
        "Added for use with unit tests."
    ),
)

TASKCLI_ADV_PRINT_RUNTIME = EnvVar(
    default_value="false",
    desc=("If set to true, prints the total exection time the tool (not including the ython interpreter startup). "),
)


def _set_names() -> None:
    """Use the variable name to set the 'name' property of the EnvVar objects defined in this module.

    This way we don't have to duplicate the name in two places.
    """
    for name, value in globals().items():
        if isinstance(value, EnvVar):
            value.name = name


def show_env(verbose: int) -> None:
    """Print the environment variables used by taskcli."""
    print("# Environment variables used by taskcli:", file=sys.stderr)  # noqa: T201

    for name, value in globals().items():
        if isinstance(value, EnvVar):
            color = ""
            clear = ""
            green = ""
            green = configuration.colors.green
            clear = configuration.colors.end
            dark = configuration.colors.dark_gray
            if value.value != value.default_value:
                color = configuration.colors.yellow
            print(f"{green}{name}{clear}={color}{value.value}{clear}")  # noqa: T201
            if value.desc and verbose:
                print(f"{dark}{value.desc}{clear}")  # noqa: T201


_set_names()
