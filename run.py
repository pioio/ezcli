from dataclasses import dataclass
from sys import stderr
import time
import sys
@dataclass
class RunResult:
    """Help"""
    exit_code: int

import subprocess
def run(cmd, check=True) -> RunResult:
    BLUE = "\033[94m"
    END = "\033[0m"
    print(f"{BLUE}@@ {cmd}{END}")
    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()
    exit_code = popen.returncode

    if check and exit_code != 0:
        RED = "\033[91m"
        ENDC = "\033[0m"
        sys.stdout.flush()
        sys.stderr.flush()
        print(f"{RED}Command failed with exit code {exit_code}{ENDC}\n", stderr, flush=True)
        raise Exception(f"Command failed with exit code {exit_code}")
    return RunResult(exit_code=exit_code)