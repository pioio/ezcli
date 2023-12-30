import pytest

from taskcli import run
from taskcli.runcommand import RunError


def test_run_command():
    run("date")
    run("date", check=True)


def test_run_command_check():
    with pytest.raises(SystemExit):
        run("/bin/false", check=True)
