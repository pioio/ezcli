"""Examples how to troubleshoot taskcli.

Run:
- t -f FILENAME debug-a-task
- t -f FILENAME list-tasks
- t -f FILENAME debug-config | head -10   # print the first 10 lines of the config fields
"""

from taskcli import tt, task

# This will pretty print the all settings current config AFTER your
# custom env vars and cli args have been applied.
# I.e. this is typically what you want to use
@task
def debug_config():
    """Print all settings of current config."""
    tt.config.debug() # you can pass it a function which you want to use to print

@task
def debug_a_task():
    """Print detailed info about a specific task.

    Can also be used for tasks included from other file.
    """
    thetask = tt.get_task("debug-a-task")
    thetask.debug()

@task
def list_tasks():
    """List all available tasks."""
    for t in tt.get_tasks():
        print(f"{t.name=}, {t.hidden=}")


# Alternatively, calling tt.config.debug() in the global scope
# will pretty print all setting of current config BEFORE env vars
# and cli args have been applied.
# Example:
# tt.config.debug()

# Finally, you can always run with  "-v", "-vv", or "-vvv" to get more debug info.
