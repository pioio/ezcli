import pytest

from taskcli import envvars
from taskcli.envvar import EnvVar


@pytest.mark.skip()
def test_envvars():
    envvars.show_env(1)
    envvars.show_env(0)

    extra = [EnvVar("FOO", "bar"), EnvVar("BAR", "baz")]
    envvars.show_env(1, extra)

    env_var = EnvVar("FOO", "bar")
    assert env_var.pretty() == "FOO=bar"
    env_var.log_debug()

    assert env_var.value == "bar"

    assert env_var.is_true() is False

    env_var = EnvVar("FOO", "true")
    assert env_var.is_true() is True
