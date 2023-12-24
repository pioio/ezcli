from dataclasses import dataclass
from sys import stderr
import time
import sys
import inspect
from typing import Any
@dataclass
class RunResult:
    """Help"""
    exit_code: int

import os
import subprocess

def _get_location() -> str:
    frame = inspect.currentframe().f_back.f_back
    module = inspect.getmodule(frame)
    filename = module.__file__
    lineno = frame.f_lineno
    location = f"{filename}:{lineno}"
    return location

class RunException(Exception):
    def __init__(self, *args:Any, exit_code:int):
        super().__init__(*args)
        self.exit_code = exit_code
    pass


def run(cmd, check:bool=True, exit_on_fail:bool=True) -> RunResult:
    try:
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
            msg = f"Command failed with exit code {exit_code}"
            raise RunException(msg, exit_code=exit_code)

        return RunResult(exit_code=exit_code)
    except RunException as e:
        sys.exit(e.exit_code)