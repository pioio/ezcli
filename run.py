from dataclasses import dataclass
from sys import stderr
import time
import sys
import inspect
@dataclass
class RunResult:
    """Help"""
    exit_code: int

import os

def _get_location() -> str:
    frame = inspect.currentframe().f_back.f_back
    module = inspect.getmodule(frame)
    filename = module.__file__
    lineno = frame.f_lineno
    location = f"{filename}:{lineno}"
    return location

import subprocess
def run(cmd, check=True) -> RunResult:
    BLUE = "\033[94m"
    END = "\033[0m"
    BLACK = "\033[30m"
    if not os.environ.get("TASKCLI_LOCATION", "") == "1":
        location = f" {BLACK}({_get_location()}){END}"
    else:
        location = ""



        print(f"{BLUE}@@ {cmd}{END}{location}", flush=True, file=stderr)

    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()
    exit_code = popen.returncode

    if check and exit_code != 0:
        RED = "\033[91m"
        ENDC = "\033[0m"
        sys.stdout.flush()
        sys.stderr.flush()
        print(f"{RED}Command failed with exit code {exit_code}{ENDC} {location}", flush=True, file=stderr)
        raise Exception(f"Command failed with exit code {exit_code}")
    return RunResult(exit_code=exit_code)