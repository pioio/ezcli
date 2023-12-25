import nox


@nox.session(python=["3.10", "3.11", "3.12"])
def test(session):
    session.install(".", "pytest")
    session.run("pytest", "tests/")
