"""(Some) environment variables used by taskcli.

The options listed in this file can only be set via the environment.
They cannot be set via the command line.
Thus, they can be seen as universal global settings.
Typically you will never have to change those. But you can, if you need to.

Sidenote: The TaskCLIConfig object contains the remaining configuration options which can be
set not only via the environment, but also via other means (e.g. CLI arguments).
These are the options which are more likely to be changed by the user.
"""
import logging
import sys

from taskcli import configuration

from .envvar import EnvVar

from .logging import get_logger
log = get_logger(__name__)

TASKCLI_TASKS_PY_FILENAMES = EnvVar(
    default_value="tasks.py",
    desc="Comma separated list of filenames which 'taskcli' tool should include by default.",
)

TASKCLI_EXTRA_TASKS_PY_FILENAMES = EnvVar(
    default_value="../tasks.py,../../tasks.py,../../../tasks.py,../../../../tasks.py,../../../../../tasks.py,../../../../../../tasks.py ",
    desc=("Comma separated list of filepaths which 'taskcli' tool should include "
           "by default, and combine with tasks from the locally-present `task.py` file."),
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
        "Comma separated list of Taskfiles.dev filenames from which to include additional tasks. "
        "TASKCLI_GOTASK_TASK_BINARY_FILEPATH must be set for this to work. "
        "This is useful if you already have some tasks in Taskfile.yaml format, and want to run them with `taskcli`."
    ),
)

TASKCLI_GOTASK_TASK_NAME_PREFIX = EnvVar(
    default_value="tf.", desc=("String to prefix to all task names from a Taskfile.dev yaml file. ")
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

TASKCLI_TAG_FOR_IMPORTANT_TASKS = EnvVar(
    default_value="imp",
    desc=(
        "The tag string automatically assigned to important tasks. "
        "Important tasks can be then listed with 'tt -t <tag>'."
    ),
)


def _set_names() -> None:
    """Use the variable name to set the 'name' property of the EnvVar objects defined in this module.

    This way we don't have to duplicate the name in two places.
    """
    for name, value in globals().items():
        if isinstance(value, EnvVar):
            value.name = name


def show_env(verbose: int, extra_vars: list[EnvVar] | None = None) -> None:
    """Print the environment variables used by taskcli."""
    print("# Environment variables used by taskcli:", file=sys.stderr)  # noqa: T201

    extra_vars = extra_vars or []
    env_vars_to_list = []
    for _, value in globals().items():
        if isinstance(value, EnvVar):
            env_vars_to_list.append(value)
    env_vars_to_list.extend(extra_vars)

    for value in env_vars_to_list:
        if isinstance(value, EnvVar):
            name = value.name
            color = ""
            clear = ""
            green = ""
            green = configuration.colors.green
            clear = configuration.colors.end
            dark = configuration.colors.dark_gray
            if value.value != value.default_value:
                color = configuration.colors.yellow

            desc = ""
            if value.desc and verbose:
                desc = f"  {dark}# {value.desc}{clear}"
            print(f"{green}{name}{clear}={color}{value.value}{clear}{desc}")  # noqa: T201


_set_names()
