"""Entrypoint for the 'taskcli' command."""

import sys
import os


TASKCLI_TASKFILE_FILENAMES_ENV_VAR_NAME = "TASKCLI_TASKFILE_FILENAMES"
TASKCLI_TASKFILE_FILENAMES = os.environ.get(
    TASKCLI_TASKFILE_FILENAMES_ENV_VAR_NAME, "project.py, tasks.py, taskfile.py"
)


def main() -> None:
    """Entrypoint for the 'taskcli' command."""
    from taskcli import dispatch

    try:
        import taskcli
    except ImportError:
        print("'taskcli' module is not installed, please install it with 'pip install taskcli'")
        sys.exit(1)

    for filename in TASKCLI_TASKFILE_FILENAMES.split(","):
        filename = filename.strip()
        if os.path.exists(filename):
            sys.path.append(os.getcwd())
            import tasks

            taskcli.include(tasks)
            taskcli.dispatch()
            return

    # TODO, check upper dirs
    print(
        f"No tasks file found in current directory, looked for: {', '.join(TASKCLI_TASKFILE_FILENAMES)}. "
        f"Change the environment variable {TASKCLI_TASKFILE_FILENAMES_ENV_VAR_NAME} to change the "
        "list of filenames to look for."
    )
    sys.exit(1)
