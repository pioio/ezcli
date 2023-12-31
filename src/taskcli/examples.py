"""Contains all the taskcli code examples.

Code examples are defined as classes.

- code of each example is integration tested for basic functionality (written to a tasks.py, and ran).
  (this might also adds some common headers/footers to the code to make it runnable, to keep the example short)
- the documentation
- the `taskcli --examples` output


"""

import dataclasses
from codecs import replace_errors
from dataclasses import dataclass
from os import replace

from . import configuration

SEPARATOR = "### "


def _border(text: str) -> str:
    import os

    columns = 120 if not os.isatty(1) else os.get_terminal_size().columns
    terminal_width = min(columns, 120)
    text = f"{SEPARATOR}{text}         ".ljust(terminal_width - 1, " ")
    return f"{configuration.colors.green}{configuration.colors.underline}{text} {configuration.colors.end}"


def print_examples() -> None:
    """Print all examples to stdout."""
    lines = ""
    for example in get_examples():
        lines += _border(example.title) + "\n"

        if example.desc:
            for line in example.desc.split("\n"):
                lines += "# " + line + "\n"
        lines += example.text + "\n"

    color = configuration.colors
    colorized = []
    for line in lines.split("\n"):
        if line.startswith("@task"):
            line = color.white + line + color.end
        if line == "    pass":
            line = color.dark_gray + line + color.end
        if line.startswith("#"):
            line = color.green + line + color.end
        colorized.append(line)

    text = "\n".join(colorized)
    print(text)  # noqa: T201


@dataclass
class Example:
    """Example of a tasks.py."""

    title: str
    text: str
    desc: str = ""


PINK = "@@PINK@@"
BLUE = "@@BLUE@@"
HL = "@@HL@@"
END = "@@END@@"


def format_text_to_console(example: Example) -> str:
    """Format the text to console."""
    return _replace_colors(_get_terminal_colors(), example.text)

def format_text_strip_colors(example: Example) -> str:
    no_colors = _get_terminal_colors()
    no_colors = {k: "" for k in no_colors}
    return _replace_colors(no_colors, example.text)


def format_text_to_markdown(example: Example) -> str:
    return format_text_strip_colors(example)


def _get_terminal_colors():
    terminal_colormap = {
        PINK: configuration.colors.pink,
        BLUE: configuration.colors.blue,
        HL: configuration.colors.yellow + configuration.colors.underline,
        END: configuration.colors.end,
    }
    return terminal_colormap


def _replace_colors(colormap: dict[str, str], text: str) -> str:
    """Replace colors in text."""
    for m in colormap:
        text = text.replace(m, colormap[m])
        text = text.replace(m.lower(), colormap[m])
    return text


def get_examples() -> list[Example]:
    """Get all examples.

    All examples are unit tested for basic functionality.

    """
    return [
        Example(
            title="basic",
            text=f'''# To define a task, simply add the @task decorator to a function,
# and then run `taskcli foo <args>` to run that function
# The first line of docstring is used as the description of the task when you run `taskcli`.
from taskcli import task

{HL}@task{END}
def foo():
    """This lines ends up as the list output.

    This line is not shown in the list outpu
    """
    print(a + b)
''',
        ),
        Example(
            title="arguments",
            text=f'''#

@task
def task1({BLUE}age{END}: int, {BLUE}name{END}: str = "alice"):
    """This task has two {BLUE}positional{END} arguments, one of them optional."""
    pass

@task
def hello2({BLUE}height{END}: int=42, {HL}*{END}, {PINK}person{END}: str = "john"):
    """This task has one {BLUE}positional{END}, and one {PINK}optional{END} argument.
    Args after the "{HL}*{END}" are named only.
    call with: taskcli hello2 {BLUE}25{END} {PINK}--name person{END}"""
    pass
    ''',
        ),
        Example(
            title="aliases",
            text=f"""# Aliases can be defined as strings, or iterable of strings

@task({HL}aliases="t1"{END})
def task1():
    pass

@task({HL}aliases=("t2","foobar"){END})
def task2():
    pass
""",
        ),
        Example(
            title="Customize tasks base on custom conditions",
            desc="""
You can batch customize the tasks programmatically,
For example to add a default argument to all tasks.
For example, you can append a custom tag to all tasks with a certain name pattern
Example below adds the tag "prod" to all tasks with "prod" in their name, marks them as important, as makes
them the listed in red.
            """,
            text=f"""
from taskcli import Task, tt, task

@task
def {PINK}deploy_to_prod{END}():
    pass

tasks:list[Task] = {HL}tt.get_tasks(){END}
for t in tasks:
    if "prod" in {PINK}t.name{END}:
        t.important = True
        t.tags += ["prod"]
        t.name_format = "{{red}}{{name}}{{clear}}"
""",
        ),
    ]
