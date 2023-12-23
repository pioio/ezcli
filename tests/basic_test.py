from taskcli import task, run_task

def test_foobar():
    def x(z:int|None|list[str]):
        pass

    with (
         open("/tmp/foobar", "w") as foobar,
        open("/tmp/foobar", "r") as foobar2,
    ):
        pass

def test_basic():
    x = 0
    @task
    def foobar() -> int:
        nonlocal x
        x += 1
        return 42

    assert foobar() == 42
    assert x == 1

    run_task(argv=["foobar"])
    assert x == 2