import inspect
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from sys import stderr
from typing import Any


@dataclass
class RunResult:
    """The result of a run command."""

    exit_code: int


def _get_location() -> str:
    frame = inspect.currentframe()
    assert frame is not None
    frame = frame.f_back
    assert frame is not None
    frame = frame.f_back
    module = inspect.getmodule(frame)
    assert module is not None
    filename = module.__file__

    assert frame is not None
    lineno = frame.f_lineno
    location = f"{filename}:{lineno}"
    return location


class RunError(Exception):
    """An error occurred while running a command."""

    def __init__(self, *args: Any, exit_code: int):
        super().__init__(*args)
        self.exit_code = exit_code


def run(cmd: str, check: bool = True) -> RunResult:
    """Run a command."""
    try:
        BLUE = "\033[94m"
        END = "\033[0m"
        BLACK = "\033[30m"
        if not os.environ.get("TASKCLI_LOCATION", "") == "1":
            location = f" {BLACK}({_get_location()}){END}"
        else:
            location = ""

            print(f"{BLUE}@@ {cmd}{END}{location}", flush=True, file=stderr)  # noqa: T201

        popen = subprocess.Popen(cmd, shell=True)
        popen.communicate()
        exit_code = popen.returncode

        if check and exit_code != 0:
            RED = "\033[91m"
            ENDC = "\033[0m"
            sys.stdout.flush()
            sys.stderr.flush()
            print(f"{RED}Command failed with exit code {exit_code}{ENDC} {location}", flush=True, file=stderr)  # noqa: T201
            msg = f"Command failed with exit code {exit_code}"
            raise RunError(msg, exit_code=exit_code)

        return RunResult(exit_code=exit_code)
    except RunError as e:
        sys.exit(e.exit_code)
