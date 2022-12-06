#!/usr/bin/env python

from click import pass_context
from taskcli import SETTINGS

from taskcli import group, option, argument, SETTINGS
import functools

################################################################################
# Example of tweaking the defaults

# Set to zero to always print arguments on a new line
# Set to -1 to never print them on the new line
# The default is fold them to a new line if the line is too long
# SETTINGS["short_help_fold_args_to_new_line_after"] = 0


# Option shared between multiple commands
def option_dry_run(func):
    @option("--dry-run", "-d", is_flag=True, help="Dry run", required=False)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@group()
def cli():
    """This is the main cli group"""
    pass


################################################################################
# Other commands




@cli.command("add")
@argument("number_a", type=int)
@argument("number_b", type=int)
@pass_context
def add(ctx, number_a, number_b):
    """Add two numbers."""
    print(number_a + number_b)


@cli.command()
@pass_context
def many_adds(ctx):
    ctx.invoke(add, number_a=2, number_b=2)
    ctx.invoke(add, number_a=4, number_b=4)
    ctx.invoke(add, number_a=6, number_b=6)



@cli.command("temperature", aliases="temp")
@argument("city", required=True, metavar="CITY_NAME")
def check_temperature_in_city_with_curl(city):
    """Check temperature in a city."""
    import subprocess
    import json

    weather = subprocess.check_output(
        ["curl", "-s", f"https://wttr.in/{city}?format=j1"]
    )
    temperature = json.loads(weather)["current_condition"][0]["temp_C"]
    print(temperature)


################################################################################
# File commands


@group("file", aliases=["f", "fi"])  # multiple aliases (an iterable)
def cli_file():
    """Operate on files."""
    pass


cli.add_command(cli_file)


@cli_file.command("create", aliases="c")  # single alias (a string)
@argument("filename", required=True)
@option_dry_run
def create_file(filename, dry_run):
    """Create a new file."""
    print(f"Creating a file {filename}")


@cli_file.command("remove", aliases=["r", "rm"])
@argument("filenames", nargs=-1, required=True)
@option("--force", "-f", is_flag=True, default=False)
@option_dry_run
def remove_files(filenames, force, dry_run):
    """Remove one or more files."""
    print(f"Removing {filenames} with force={force}, dry_run={dry_run}")


@cli_file.command("move")
@argument("filename_src", required=True)
@argument("filename_dst", required=True)
@option_dry_run
def move_file(filename_src, filename_dst, dry_run):
    """Move a single file."""
    print(f"moving a file {filename_src} to {filename_dst}")


@group("update", aliases=["u"])
def update_file():
    """Different ways to update a file."""
    pass


cli_file.add_command(update_file)


@update_file.command("content", aliases=["c"])
@argument("filename", required=True)
@argument("content", required=True)
@option_dry_run
def file_update_content(filename, content, dry_run):
    """Update the content."""
    print(f"Updating content of {filename} to {content}")


@update_file.command("mtime", aliases=["m"])
@argument("filename", required=True)
@option("--timestamp", "mtime", required=True)
@option_dry_run
def file_update_mtime(filename, mtime, dry_run):
    """Update the modification time."""
    print(f"Updating mtime of {filename} to {mtime}")


################################################################################
# Greet commands


@group("greet", aliases="g")
def cli_greet():
    """Commands that print a greeting."""
    pass


cli.add_command(cli_greet)


@cli_greet.command(aliases=["u"])
@argument("username", default="unknown user", required=False)
def user(username):
    """Greet the user"""
    print(f"Hello, {username}!")


@cli_greet.command(aliases=["sh"])
@option("--message", default="Hello", required=False)
def say_hello(message):
    """Print a greeting message."""
    print(f"{message}!")


@cli_greet.command("multiple-times")
@option("--message", default="Hello", required=False)
@option("--count", "-c", required=True, type=int)
def greet_multiple_times(message, count):
    """Print a message multiple times."""

    for i in range(count):
        print(f"{message}!")


if __name__ == "__main__":
    cli()
