from typing import Any
from .utils import get_callers_module, get_module

from .types import Module, Callable

from dataclasses import dataclass
from .task import Task

@dataclass
class ModuleSettings:
    """Settings specific to a module, and used only if that module is the main task."""
    include_parent: bool = False
    parent_task_filter: Callable[[Task], bool] | None = None
    init_fun: Callable[[Task], bool] | None = None
    #parent_filter

module_settings: dict[Module, ModuleSettings] = {}

def get_module_settings(module: Module) -> ModuleSettings:
    if module not in module_settings:
        module_settings[module] = ModuleSettings()
    return module_settings[module]

def reset():
    module_settings.clear()


def set_module_init_function(fun: Callable[..., Any]) -> None:
    """Set the function to be called after the module is initialized.

    This function will called only once, and for the main taskfile.
    I.e. it will not be called for any modules/taskfile you tt.include()

    Useful if you want to customize tt.config object, but don't want included modules
    to override your settings.
    """
    module = get_callers_module()
    get_module_settings(module).init_fun = fun