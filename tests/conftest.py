# Uncomment for a different way of rendering whitespace
# Ref: https://stackoverflow.com/questions/74663915/pytest-show-whitespace-and-tabs-in-errors

# TAB_REPLACEMENT = "[tab]"
# SPACE_REPLACEMENT = "[space]"
# def pytest_assertrepr_compare(config, op, left, right):
#     left = left.replace(" ", SPACE_REPLACEMENT).replace("\t", TAB_REPLACEMENT)
#     right = right.replace(" ", SPACE_REPLACEMENT).replace("\t", TAB_REPLACEMENT)
#     return [f"{left} {op} {right} failed!"]