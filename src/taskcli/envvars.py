"""Environment variables used by taskcli."""
import logging
import os

from .envvar import EnvVar
#from .taskfiledev import go_task_project_name

log = logging.getLogger(__name__)

TASKCLI_TASKS_PY_FILENAMES = EnvVar(
    default_value="tasks.py",
    desc="Comma separated list of filenames which 'taskcli' tool should include by default.",
)

TASKCLI_GOTASK_TASK_BINARY_FILEPATH = EnvVar(
    default_value="",
    desc="The absolute path to the binary of the taskfile.dev tool. Used to include tasks from Taskfile.yaml files.",
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
    default_value="false", desc=("If set to true, overrides formatting options to make the listing output simpler. "
                                 "Added for use with unit tests.")
)


def _set_names() -> None:
    """Use the variable name to set the 'name' property of the EnvVar objects defined in this module.

    This way we don't have to duplicate the name in two places.
    """
    for name, value in globals().items():
        if isinstance(value, EnvVar):
            value.name = name


_set_names()
