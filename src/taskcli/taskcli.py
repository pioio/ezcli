# This is a small library which wraps around `click`
# and extends some of its classes.
#
# It changes the default click behavior, and its help/usage formatting, to
# better accomodate creating small, task-like, functions.
#
# It optimizes the default help/usage output for
# information density, and readability.
# Specifically, the printed usage shows all the arguments that can be used for each invocation,
# shows their defaults, and color codes them dependin on whether
# they are mandatory or not.
#
# Resources helpful in creating the code below:
# Adding aliases to click:
#   https://stackoverflow.com/questions/46641928/python-click-multiple-command-names
# Changing command order:
#   https://stackoverflow.com/questions/47972638/how-can-i-define-the-order-of-click-sub-commands-in-help
#

import collections

import click
from click import argument
from click.core import Context
from click.formatting import HelpFormatter


# After import this library, you can tweak certain settings here to modify
# the behavior of the library.
SETTINGS = dict(
    # After this many characters,
    # the default usage text  will be truncated with "..."
    # Special values:
    #  -1: never fold (can result in long lines)
    #   0: hide human text altogether
    short_help_max_length=70,
    # After exceeding many characters the usage help line will expand to two lines,
    # The second line will contain only the arguments
    short_help_fold_args_to_new_line_after=60,
    # Whether or not to print default values for some arguments
    # (The default values are not printed for all possible parameter types)
    short_help_print_default_values=True,
    # Whether or not to print default value in the full ("-h") output of
    # a command.
    long_help_print_default_values=True,
    # Context settings passed to the 'click' library by default.
    click_context_settings=dict(
        help_option_names=["-h", "--help"], max_content_width=160
    ),
)


# Color values for coloring text
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class OrderedGroup(click.Group):
    def __init__(self, aliases=None, sorted=False, name=None, commands=None, **attrs):
        """
        aliases: list of aliases for this group
        sorted: if True, the commands will be sorted by name when printing help
        """

        # Allow for passing a string
        if type(aliases) == str:
            aliases = [aliases]

        super(OrderedGroup, self).__init__(name, commands, **attrs)

        self.commands = commands or collections.OrderedDict()

        # Special property for storing the names of aliases of the command
        self.taskcli_aliases = aliases

        self.taskcli_sorted = sorted

        self.taskcli_group_aliases = []
        if aliases:
            for alias in aliases:
                g = OrderedGroup(name=alias, commands=self.commands, aliases=None)
                g.hidden = True
                self.taskcli_group_aliases.append(g)

    def add_command(self, cmd, name=None):
        if not name:
            name = cmd.name
        # print ("adding command: ", cmd.name, " to command", self.name)
        # 1) add the command to this group
        super(OrderedGroup, self).add_command(cmd, name)

        # 2) add the command to all of this group's aliases
        if "taskcli_group_aliases" in self.__dict__:
            for alias in self.taskcli_group_aliases:
                alias.add_command(cmd, name=name)

        # 3) add aliases of the command to this group
        if "taskcli_group_aliases" in cmd.__dict__:
            for alias in cmd.taskcli_group_aliases:
                self.add_command(alias, name=alias.name)
        # 4)
        if (
            "taskcli_group_aliases" in cmd.__dict__
            and "taskcli_group_aliases" in self.__dict__
        ):
            for group_alias in self.taskcli_group_aliases:
                for command_alias in cmd.taskcli_group_aliases:
                    group_alias.add_command(command_alias, name=command_alias.name)

    def command(self, *args, aliases=None, **kwargs):
        """Behaves the same as `clickt.command()` except it
        supports "aliases" keyword argument.

        Creats a hidden command with that name
        """

        # Allow for passing a string
        if type(aliases) == str:
            aliases = [aliases]

        def decorator(f):
            # print("Decorator!")
            """Called when adding a command to the group.
            If group has aliases, create a hidden command for each alias
            """

            # 1) create the command for this group
            cmd = super(OrderedGroup, self).command(*args, **kwargs)(f)
            cmd.taskcli_aliases = aliases

            # 2) add the new command to all of this group's aliases
            if "taskcli_group_aliases" in self.__dict__:
                # now dd this command to all the aliases of the group
                for galias in self.taskcli_group_aliases:
                    galias.add_command(cmd, name=cmd.name)

            if aliases:
                # create aliases for the command
                cmd_aliases = []
                for alias in aliases:
                    trimmed_args = args

                    # we need overrider the name. So, if it was specified, remove it
                    # so that we can replace it with an alias
                    if len(args) > 0:
                        trimmed_args = args[1:]  # remove first, "name", argument
                    if "name" in kwargs:
                        del kwargs["name"]

                    # 3) add the aliases to this group
                    # This created the alias (a), and also adds it to this group.
                    # we store the created alias to later in (4) add it to all of this group's aliases
                    a = super(OrderedGroup, self).command(
                        name=alias, *trimmed_args, **kwargs
                    )(f)
                    a.hidden = True
                    a.name = alias
                    cmd_aliases.append(a)

                    # Make aliases share some fields with the main command
                    # This way when we later decorate the command
                    # with decorators line @parameter, @option, etc.
                    # the params of the aliases will also get those.
                    # Without this, doing things like ``./cli.py mygroup c --arg foo `  will
                    # not work - the alias will behave as if it did not have options defined
                    # FIXME: this needs to be fixed for groups arguments, and for any other decorattors that modify the command,
                    a.params = cmd.params

                # 4) add the aliases to all of this group's aliases
                if "taskcli_group_aliases" in self.__dict__:
                    for galias in self.taskcli_group_aliases:
                        for calias in cmd_aliases:
                            galias.add_command(calias, name=calias.name)

            return cmd

        return decorator

    def list_commands(self, ctx):
        return self.commands if not self.taskcli_sorted else sorted(self.commands)

    def format_options(self, ctx: Context, formatter: HelpFormatter) -> None:
        # super().format_options(ctx, formatter)
        self.format_commands(ctx, formatter)

    def get_commands_to_display(self, ctx: Context):
        """Returns a list of commands/tasks to display in the help text.
        This is not a overriding function.

        Filters out hidden commands (aliases).
        """
        commands = []

        def add_subcommands(cmd, indent=1):
            # List subcommands of the subcommand
            if "list_commands" in dir(cmd):
                for subcommand2 in cmd.list_commands(ctx):
                    cmd2 = cmd.get_command(ctx, subcommand2)
                    # What is this, the tool lied about a command.  Ignore it
                    if cmd2 is None:
                        continue
                    if cmd2.hidden:
                        continue

                    if "list_commands" in dir(cmd2):
                        subcommand2 = bcolors.UNDERLINE + subcommand2 + bcolors.ENDC

                    commands.append((indent * "  " + subcommand2, cmd2))
                    add_subcommands(cmd2, indent + 1)

        add_subcommands(self, 0)
        return commands

    def format_commands(self, ctx: Context, formatter: HelpFormatter) -> None:
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        # TODO: this function needs refactoring

        commands = self.get_commands_to_display(ctx)
        if len(commands) == 0:
            return

        limit = SETTINGS["short_help_max_length"]
        fold_after: int = SETTINGS["short_help_fold_args_to_new_line_after"]
        rows = []
        second_line = ""
        index = -1

        # Iterate over all displayable commands
        # TODO: move iterating over groups to here, and compute a per-group max length, so that we can align the arguments within each group.
        for subcommand, cmd in commands:
            index += 1
            human_help_text = cmd.get_short_help_str(limit)

            if limit == 0:
                human_help_text = ""

            params = cmd.get_params(ctx)
            param_help_text = []
            for param in params:
                # We want to skip some obvious options to not clutter the usage page
                if param.name == "help":
                    continue
                if param.name == "verbose":
                    continue

                param_help_text += [get_short_help_from_param(param, ctx)]

            if fold_after and len(human_help_text) > fold_after:
                second_line = " ".join(param_help_text)
            else:
                if human_help_text:
                    human_help_text += (
                        " "  # add spacer between human text, and parameters
                    )
                human_help_text = human_help_text + " ".join(param_help_text)

            if cmd.taskcli_aliases:
                aliases = [
                    bcolors.WARNING + alias + bcolors.ENDC
                    for alias in cmd.taskcli_aliases
                ]
                subcommand = [subcommand] + aliases
                subcommand = ", ".join(subcommand)

            color = bcolors.OKGREEN
            rows.append((color + subcommand + bcolors.ENDC, human_help_text))

            if second_line:
                rows.append((" ", second_line))
                second_line = ""

        # finally, format all the rows
        if rows:
            with formatter.section(("Usage")):
                formatter.write_dl(rows)

    def format_help(self, ctx, formatter) -> None:
        """Writes the help into the formatter if it exists."""
        # self.format_usage(ctx, formatter)
        # self.format_help_text(ctx, formatter)
        self.format_options(ctx, formatter)
        # self.format_epilog(ctx, formatter)


def get_short_help_from_param(param, ctx, color=True):

    default_value = param.get_default(ctx)
    colorstart = ""
    colorend = ""
    if color:
        colorstart = bcolors.OKBLUE
        if default_value is None or param.required:
            colorstart = bcolors.FAIL
        colorend = bcolors.ENDC

    # determine the default-value string
    default_value_string = ""
    if default_value is not None and SETTINGS["short_help_print_default_values"]:
        if type(default_value) in [int, float]:
            default_value_string = str(default_value)
        if type(default_value) in [str]:
            default_value_string = f"{default_value}"
            # shorten long strings
            truncate_len = 20
            if len(default_value_string) > truncate_len:
                default_value_string = default_value_string[:truncate_len] + "..."
            default_value_string = "'" + default_value_string + "'"

    if isinstance(param, click.Argument):
        if default_value_string:
            return (
                colorstart
                + param.make_metavar()
                + "="
                + default_value_string
                + colorend
            )
        else:
            return colorstart + param.make_metavar() + colorend
    elif isinstance(param, click.Option):
        help_record = param.get_help_record(ctx)[0]

        options = param.opts + param.secondary_opts
        # we use '|' to join, as with using comma and with multiple params its
        # difficult to see which options are aliases of each other
        help_record = "|".join(options)

        if default_value_string:
            return colorstart + help_record + "=" + default_value_string + colorend
        else:
            return colorstart + help_record + colorend
    else:
        assert False


def format_usage(self, ctx, formatter):
    """Writes the usage line into the formatter if it exists.
    This is a low-level method called by `format_help`.
    """
    if self.usage is not None:
        formatter.write_usage(self.get_usage(ctx), self.get_usage_hint(ctx))


def option(*args, **kwargs):
    if "show_default" not in kwargs and SETTINGS["long_help_print_default_values"]:
        kwargs["show_default"] = True

    return click.option(*args, **kwargs)


def group(*args, **kwargs):
    """Changes the default group of click to an ordered group
    (order change does not work if commands passed as arguments)"""
    return click.group(
        *args,
        context_settings=SETTINGS["click_context_settings"],
        cls=OrderedGroup,
        **kwargs,
    )
