from taskcli.taskcliconfig import TaskCLIConfig


def test_basic():
    config = TaskCLIConfig(load_from_env=False)
    assert not config.show_hidden
