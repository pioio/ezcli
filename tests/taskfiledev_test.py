from tempfile import TemporaryDirectory
from typing import Annotated, Any, get_args, get_origin

import pytest
from pkg_resources import require

from taskcli import arg, task, tt, run
from taskcli.parameter import Parameter
from taskcli.parametertype import ParameterType
from taskcli.task import Task

from . import tools
from .tools import reset_context_before_each_test
import os


import sys
import taskcli.taskfiledev

BINARY_ENV_VAR = taskcli.envvars.TASKCLI_GOTASK_TASK_BINARY_FILEPATH.name

# TODO: skip the tests if taskfile is not installed.

def test_should_include():
    from taskcli.taskfiledev import should_include_taskfile_dev

    with taskcli.utils.change_env({BINARY_ENV_VAR: ""}):
        cliarg = tt.config.field_no_go_task.cli_arg_flag
        assert should_include_taskfile_dev(argv=[cliarg]) is False
        assert should_include_taskfile_dev(argv=[]) is False

    with taskcli.utils.change_env({BINARY_ENV_VAR: "task"}):
        assert should_include_taskfile_dev(argv=[]) is True
        assert should_include_taskfile_dev(argv=[cliarg]) is False


def test_include_taskfiledev2():
    """Generat example taskfile and try to include it"""
    with TemporaryDirectory() as tmpdir:
        with tools.change_dir(tmpdir):
            tools.run_tasks("task --init")
            content = open("Taskfile.yml").read()
            open("Taskfile.yml", "w").write(content.replace("default:", "default_foobar:"))

        # Here we also test that it will change the env as expected
        this_module = sys.modules[__name__]
        with taskcli.utils.change_env({BINARY_ENV_VAR: "task"}):
            ret = taskcli.taskfiledev.include_tasks(to_module=this_module, path=tmpdir)
            assert ret is True

            tasks = tt.get_tasks()
            assert len(tasks) == 1
            assert tasks[0].name == "tf.default_foobar"

