"""Tests the baked in code examples."""


import taskcli


def test_all_examples():
    """Test that examples listed with --examples do not have any obvious typos/errors in them.

    This does NOT test if the examples actually do what they promised.
    """
    examples = taskcli.examples.get_examples()

    for example in examples:
        print("Testing example:", example.title)
        assert example.title
        assert example.text

        shared_headers = """
from taskcli import task, include, group, dispatch, tt
"""
        shared_footers = """
if __name__ == "__main__":
    dispatch()
"""

        filename = "/tmp/taskcli-example-unit-test.py"
        with open(filename, "w") as f:
            code = taskcli.examples.format_text_strip_colors(example)
            content = shared_headers + code + shared_footers
            f.write(content)
            # chmod
        taskcli.run(f"chmod +x {filename}")
        taskcli.run(f"python {filename}")


def test_print_examples():
    taskcli.examples.print_examples()
