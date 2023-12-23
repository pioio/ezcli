import nox


@nox.session(python=["3.9", "3.10", "3.11"])
def test(session):
    session.install(".")
    session.run("python", "-m", "unittest", "discover", "-p", "*_test.py", "-s", "tests/")
