"""Tests the baked in code examples."""


import taskcli


def test_all_example():
    examples = taskcli.examples.get_examples()

    for example in examples:
        print("Testing example:", example.title)
        assert example.title
        assert example.text

        shared_headers = """
from taskcli import task, include, group, dispatch
"""
        shared_footers = """
if __name__ == "__main__":
    dispatch()
"""

        filename = "/tmp/taskcli-example-unit-test.py"
        with open(filename, "w") as f:
            content = shared_headers + example.text + shared_footers
            f.write(content)
            # chmod
        taskcli.run(f"chmod +x {filename}")
        taskcli.run(f"python {filename}")
