"""Code for opening and importing http://taskfile.dev files."""
import json
import logging
import os
import subprocess
import sys
from re import sub

import taskcli
from taskcli import task

from . import envvars, parser, utils

log = logging.getLogger(__name__)

go_task_project_name = "Taskfile.dev"


def should_include_taskfile_dev(argv: list[str]) -> bool:
    """Check if env vars are set to look for a Taskfile.dev file."""
    INCLUDE_TASKFILE_YAML: bool = bool(
        envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.value and envvars.TASKCLI_GOTASK_TASKFILE_FILENAMES.value
    )

    envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.log_debug()
    envvars.TASKCLI_GOTASK_TASKFILE_FILENAMES.log_debug()

    from taskcli import tt

    disabled_via_cli: bool = tt.config.field_no_go_task.cli_arg_flag in argv

    return INCLUDE_TASKFILE_YAML and not disabled_via_cli


def include_tasks(path: str = ".") -> bool:
    """Include tasks from a Taskfile.dev file. Returns True if tasks were included, False otherwise."""
    assert envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.value

    try:
        with utils.change_dir(path):
            taskfile_filepath = has_taskfile_dev(path)
            if not taskfile_filepath:
                return False

            log.debug(f"Found {go_task_project_name} file, including tasks from it. {taskfile_filepath}")
            taskfiledev = envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.value
            cmd = [taskfiledev, "--list-all", "--json"]
            if path != ".":
                cmd += ["--dir", path]
            try:
                output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if output.returncode != 0:
                    raise subprocess.CalledProcessError(output.returncode, cmd, output=output.stdout)
            except subprocess.CalledProcessError as e:
                lines_list = e.output.decode("utf-8").split("\n")
                lines_list = ["  " + line for line in lines_list if line.strip()]
                lines = "\n".join(lines_list)
                msg = f"Error running '{' '.join(cmd)}':\n{lines}'"
                raise TaskfileDevError(msg) from e
            output_str = output.stdout.decode("utf-8")
            return _include_tasks_json(json_string=output_str, cmd=" ".join(cmd))
    except TaskfileDevError as e:
        to_disable = _to_disable_string()
        msg = f"Warning: failed to include {go_task_project_name} tasks: " + str(e) + ". "
        utils.print_warning(msg)
        utils.print_warning(to_disable)
        return False


def _to_disable_string() -> str:
    from taskcli import tt

    return (
        f"To disable automatic inclusion of tasks {go_task_project_name} tasks, "
        f" use '{tt.config.field_no_go_task.cli_arg_flag}' or "
        f"unset the {envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.name} env var."
    )


class TaskfileDevError(Exception):
    """Error raised when there is a problem with a Taskfile.dev file."""


def _include_tasks_json(cmd: str, json_string: str, dir: str = ".") -> bool:
    try:
        tasks = json.loads(json_string)
    except json.decoder.JSONDecodeError as e:
        msg = f"Could not parse JSON output from '{cmd}'"
        raise TaskfileDevError(msg) from e

    if "tasks" not in tasks:
        msg = f"output of '{cmd}' did not contain a 'tasks' key."
        raise TaskfileDevError(msg)

    tasks = tasks["tasks"]
    tasks_were_included = False
    group = taskcli.Group(envvars.TASKCLI_GOTASK_TASK_GROUP_NAME.value)

    for task in tasks:  # noqa: F402
        if "name" not in task:
            msg = f"{go_task_project_name} output contains a task without a 'name' key."
            raise TaskfileDevError(msg)
        name = task["name"]
        desc = ""
        if "desc" in task:
            desc = task["desc"]

        prefix = envvars.TASKCLI_GOTASK_TASK_NAME_PREFIX.value
        taskfiledev = envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.value
        cmd_args: list[str] = [taskfiledev, "--dir", dir, name]

        def run_task(cmd_args: list[str] = cmd_args) -> None:
            log.debug("Running task imported from taskfile, running: " + " ".join(cmd_args))
            subprocess.run(cmd_args)

        taskcli.task(
            change_dir=False,
            group=group,
            name=prefix + name,
            desc=desc,
            is_go_task=True,
        )(run_task)

        log.debug(f"Included task: {prefix + name}")
        tasks_were_included = True

    this_module = sys.modules[__name__]
    taskcli.include(this_module)
    return tasks_were_included


def has_taskfile_dev(path: str = ".") -> str:
    """Check if local directory has a Taskfile.dev file."""
    for filename in envvars.TASKCLI_GOTASK_TASKFILE_FILENAMES.value.split(","):
        filename = filename.strip()
        filepath = os.path.join(path, filename)
        if os.path.exists(filepath):
            return filepath

    return ""
