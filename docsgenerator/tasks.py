from taskcli import task, run, tt
from . import generator

import logging
logging.basicConfig(level=logging.INFO)
DOCS_PATH = "../docs/"

@task(aliases=["all"])
def generate_all_docs():
    print("Generating all docs (TODO)")
    run("pwd")
    page_settings()

@task(aliases=["ps"])
def page_settings():
    page = generator.generate_settings()
    path = "../docs/settings.md"
    generator.write_file(path, page)




