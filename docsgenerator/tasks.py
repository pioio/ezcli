from taskcli import task, run, tt
from . import generator

@task(aliases=["all"])
def generate_all_docs():
    print("Generating all docs (TODO)")
    run("pwd")
    page_settings()

@task(aliases=["ps"])
def page_settings():
    generator.generate_settings()




