from taskcli import task, run, tt


@task(aliases=["gd"])
def generate_all_docs():
    print("Generating all docs (TODO)")
    run("pwd")

@task(aliases=["t"])
def test_documentation():
    run("pwd")