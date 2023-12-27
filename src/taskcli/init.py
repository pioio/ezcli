import os
import sys


def create_tasks_file(filepath: str) -> None:
    """Create a new baisc tasks.py file."""
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")  # noqa: T201
        sys.exit(1)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Created file {filepath}")  # noqa: T201


content = """#!/usr/bin/env python
from taskcli import task, tt

@task
def mytask() -> None:
    print("Hello, World!")

with tt.Group("mygroup"):
    @task
    def sometask() -> None:
        print("Hello from the group")

if __name__ == "__main__":
    # This 'if' statements is optional.
    # It's here just in case you want to run this script directly via './tasks.py'
    tt.dispatch()
"""
