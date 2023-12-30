"""Constants/strings used more than one place in the code. or accessed from code and unit tests.

Storing them here:
- makes the module dependencies simpler,
- will make it easier to change them in the future.
- makes unit tests less fragile (they make use of constants here)

When writing new unit test, instead of hardcoding shared
strings in unit tests, consider putting them here.
"""

ARG_SHOW_HIDDEN_SHORT = "-H"
HELP_TEXT_USE_H_TO_SHOW_HIDDEN = f"use {ARG_SHOW_HIDDEN_SHORT} to show (or run 'tt')"
TT_COMMAND_NAME = "tt"
GROUP_SUFFIX = "/"
NAMESPACE_SEPARATOR = "."
