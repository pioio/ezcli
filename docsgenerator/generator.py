from math import e
from taskcli import task, tt, taskcliconfig, examples
import taskcli
from datetime import datetime
import os
import logging
log =  logging.getLogger(__name__)

def autogen_header():
    """Return the "page was autogenerated" header."""
    #> timedate = datetime.now(tz=None).strftime("%Y-%m-%d %H:%M:%S")
    #> return f"""(This page was autogenerated by `{timedate}`, do not edit manually)\n"""
    return """(This page was autogenerated, do not edit manually)\n"""


BR = "  " # Github markdown needs two spaces for a line break

def generate_settings() -> str:
    """Generate the documentation page with all the settings."""
    config = taskcliconfig.TaskCLIConfig()

    out = "# Configuration fields\n"
    out += autogen_header()

    for field in config.get_fields():
        out += f"### {field.name}\n"
        out += f"{field.desc}{BR}\n"
        if field.env:
            out += f"{field.env_var_name}{BR}\n"
        else:
            out += f"(no env var){BR}\n"

        out += "\n"

    return out




PAGE_EXAMPLES_TEXT = """
Best way to learn is by example. Here are some ways of how to use `taskcli` along with the command output.

All of the examples below can also be found in the `examples/` directory of the project.

To run a specific example from the `examples/` dir yourself, do this:
```
cd examples/
t -f filename.py [optional-args]
```

Also, [go here for a cheat sheet](cheatsheet.md) -- it's a more concise version of some of the examples below.

"""

from taskcli.examples import Example, get_run_commands

def generate_example() -> str:
    """Generate the page with examples."""
    examples:list[Example] = taskcli.examples.load_examples("../examples/")

    out = "# Usage Examples\n"
    out += autogen_header()
    out += PAGE_EXAMPLES_TEXT

    for example in examples:
        fake_filepath =  f"examples/{example.filename}"
        out += f"### {example.title}\n"
        out += f"`{fake_filepath}`{BR}\n"
        # TODO remove docstring
        out += "```python\n"
        out += example.file_content
        if out[-1] != "\n":
            out += "\n"
        out += "```\n"

        runcmds = get_run_commands(example, filename=example.filepath)
        if runcmds:
            out += "##### Output of the above:\n"
        for runcmd in runcmds:

            simple_filename = os.path.basename(example.filepath)
            fake_cmd_line = runcmd.cmd_orig.replace("FILENAME", simple_filename)

            desc = runcmd.desc
            shell_command = f"# {fake_cmd_line}"
            if desc:
                shell_command = f"### {desc}\n{shell_command}"

            output = taskcli.examples.run_example(example, runcmd)
            if output.endswith("\n\n"):
                output = output[:-1]


            _assert_output_sane(output)

            markdown_highlight_type = "sh"
            assert output.endswith("\n")
            out += f"```{markdown_highlight_type}\n{shell_command}\n{output}```\n\n"


        out += "---\n"# horizontal line
    return out

_forbidden_strings = [
    "Traceback",
    "/Users/",
    "/home/",
    "/tmp",
    "/etc",
]


def _assert_output_sane(output:str) -> None:
    """To make sure nothing went wrong when running the example."""

    for string in _forbidden_strings:
        for line in output.split("\n"):
            if string in line:
                msg = f"Output contains a path: {string}, line: {line}"
                raise Exception(msg)

def write_file(path: str, content: str) -> None:
    assert path.startswith("../docs/")
    abs_path = os.path.abspath(path)
    with open(abs_path, "w") as f:
        f.write(content)

    log.info(f"Written file: {abs_path}")

def sanitize_svg(filepath:str) -> None:
    """Sanitize the SVG file to make it renderable by GitHub."""

    content = open(filepath).read()

    for string in _forbidden_strings:
        if string in content:
            msg = f"SVG contains forbidden string {string}"
            raise Exception(msg)

    # Change the image header -- The credits to ansitoimg tool lib are in README.md
    content = content.replace("AnsiToImg (courtesy of Rich)", "Terminal")

    open(filepath, "w").write(content)
