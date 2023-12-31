"""Code for working with taskcli code examples.

Examples are fully-functional python files in the 'examples/' directory of this repo.
All example files are tested as part of unit tests -- they are executed with
  the "Run" commands defined in the docstring of the file.
Taskcli doc generation then takes the examples and generates parts of documenation using them.

TODO: consider moving this files outside of the taskcli package.
"""


from dataclasses import dataclass
import subprocess

import os
from .logging import get_logger
import taskcli

from . import utils


log = get_logger(__name__)


@dataclass
class Example:
    """Example of a tasks.py files.

    Represents a example loaded from the 'examples/' directory of this repo.

    Used to generate docs/examples.md.
    """

    title: str
    file_content: str
    desc: str = ""
    filepath: str = ""

    module: object = None

    @property
    def dirpath(self):
        return os.path.dirname(self.filepath)
    @property
    def filename(self):
        return os.path.basename(self.filepath)



@dataclass
class RunCommand:
    """A command to run on an example."""

    desc: str
    cmd: str
    cmd_orig: str = ""


def get_run_commands(example: Example, filename: str) -> list[RunCommand]:
    """Extract the commands to run th example with from the docstring of the file containing the example."""
    entries: list[str] = []
    in_run_section = False
    for line in example.desc.split("\n"):
        if line.lower().startswith("run:"):
            in_run_section = True
            continue
        if line.strip() == "":  # End of section
            in_run_section = False
            continue
        if in_run_section:
            if line.lstrip().startswith("- "):
                cmd = line[1:].strip()
                entries.append(cmd)

    out: list[RunCommand] = []
    for entry in entries:
        if "#" in entry:
            cmd, desc = entry.split("#")
        else:
            cmd = entry
            desc = ""

        assert "FILENAME" in cmd
        cmd_orig = cmd
        cmd = cmd.replace("FILENAME", filename)
        out.append(RunCommand(desc=desc.strip(), cmd=cmd.strip(), cmd_orig=cmd_orig.strip()))

    return out


def load_examples(dirpath: str) -> list[Example]:
    """Discover python files in the given directory, and load them as examples."""
    assert os.path.isdir(dirpath), f"cwd: {os.getcwd()}"

    out: list[Example] = []
    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        filepath = os.path.abspath(filepath)
        log.debug("Checking %s", filepath)
        if not os.path.isfile(filepath):
            log.debug("  Not a file")
            continue
        if not filepath.endswith(".py"):
            log.debug("  Not a python file")
            continue
        log.debug("Found example: %s", filepath)
        out += [load_example(filepath)]

    if not out:
        msg = f"No examples found in {dirpath}"
        raise ValueError(msg)
    return out



def load_example(filepath: str) -> Example:
    """Load a single example from a python file by importing the module and inspecting it."""
    assert filepath.startswith("/")

    example_name = filepath_to_title(filepath)

    source = open(filepath).read()
    with utils.randomize_filename(filepath) as new_filepath:  # to get a ranadom module name
        module = utils.import_module_from_filepath(new_filepath)

    e = Example(
        title=example_name,
        file_content=source,
        desc=module.__doc__,
        filepath=filepath,
        module=module,
    )
    return e


def filepath_to_title(filepath: str) -> str:
    """Convert a filepath to a title."""
    return os.path.basename(filepath).replace(".py", "").replace("_", " ").title()


#########################


def run_example(example: Example, runcmd: RunCommand) -> str:
    """Run a single example. Return merged stdout and stderr.

    Tries to do it in a clean environment, to avoid
    poluting the output with settings from the local environment.
    - cleans TASKCLI_ env vars
    - changes to the example dir
    - disabled mer
    """
    oldcwd = os.getcwd()
    oldenv = os.environ.copy()
    try:
        # change to example dir to avoid risking poluting the context with the local environment
        os.chdir(example.dirpath)
        # TOD: clean TASKCLI env

        # remove any taskcli env vars that might be set right now from the dev env
        # TODO: run in docker container instead
        for k in list(os.environ.keys()):
            if k.startswith("TASKCLI_"):
                del os.environ[k]

        # Prevent loading extra tasks in the rare case the example file
        # sets the tt.config property to load the extra tasks and list them
        # otherwise irrelevant tasks could be included in the output
        # TODO: We should simply run this in a docker container instead.
        os.environ[taskcli.envvars.TASKCLI_EXTRA_TASKS_PY_FILENAMES.name] = "___do_not_load_extra_tasks___"

        res = subprocess.run(f"{runcmd.cmd}", shell=True, check=False, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

        if res.returncode != 0:
            print(f"Error running example: {example.title}")
            print(f"  cmd: {runcmd.cmd}")
            print(f"  desc: {runcmd.desc}")
            PINK = "\033[0;35m"
            CLEAR = "\033[0m"
            print(f"  stdout and stderr: \n{PINK}{res.stdout.decode('utf-8')}{CLEAR}")
            print(f"  returncode: {res.returncode}")
            raise ValueError("Error running example")
        stdout = res.stdout.decode("utf-8")
    finally:
        os.chdir(oldcwd)
        # Restore env
        os.environ.clear()
        os.environ.update(oldenv)

    return stdout


def get_examples() -> list[Example]:
    return load_examples("examples/")
