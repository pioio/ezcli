def param_to_cli_option(arg:str) -> str:
    """Convert foo_bar to --foo-bar, and g to -g"""
    if len(arg) == 1:
        return "-" + arg.replace("_", "-")
    else:
        return "--" + arg.replace("_", "-")
