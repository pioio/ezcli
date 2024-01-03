from re import A
from typing import Any, Generic, TypeVar, Type

T = TypeVar("T")
import json
class AdvField(Generic[T]):
    def __init__(self, value: T, desc: str = "", type_: Type|None = None, env: bool = False):
        self.value = value
        self.desc = desc
        self.type = type_ if type_ else type(value)
        self.env = env
        self.name = "unset"

    def __get__(self, obj: Any, type: Any = None) -> T:
        return getattr(obj, '_' + self.name, self.value)

    def __set__(self, obj: Any, value: T) -> None:
        setattr(obj, '_' + self.name, value)

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name

    def get_env_name(self, obj: Any) -> str:
        print("get_env_name", self.name, obj)
        return "TASKCLI_ADV_" + self.name.upper()

    def cast(self, value: str) -> T:
        if self.type == list:
            return json.loads(value)
        elif self.type in [int, float, bool]:
            return self.type(value)

        raise Exception(f"Unhandled type {self.type}")
        return value  # Fallback for strings and unhandled types

import os


class AdvancedConfig:
    render_color = AdvField("blue", "this is the render color")
    count = AdvField(4, "this is the render color", env=True)
    numbers = AdvField(["xxx", "zz"], "this is the render color")

    def set_from_env(self) -> None:
        for name, field in vars(AdvancedConfig).items():
            if isinstance(field, AdvField):
                env_name = field.get_env_name(self)
                # cast to the T type of the field ??!?!?
                print(env_name)
                if env_name in os.environ:
                    value = field.cast(os.environ[env_name])
                    setattr(self, name, value)

    def add_to_env(self):
        for name, field in vars(AdvancedConfig).items():
            if isinstance(field, AdvField):
                value = getattr(self, name)
                print("Adding to env", name, value)


cfg = AdvancedConfig()
cfg.render_color = "red"
cfg.count = 999
cfg.add_to_env()
#cfg.set_from_env()
cfg.count += 5
print("----------------")
# Iterate over fields  and print their name and description
for attr_name, attr_value in AdvancedConfig.__dict__.items():
    if isinstance(attr_value, AdvField):
        instance_value = getattr(cfg, attr_name)
        print(f"Field Name: {attr_name}, Value: {instance_value}, Description: {attr_value.desc}")


print("----------------")