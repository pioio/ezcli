from taskcli import task, run, tt
import taskcli
import generator

import logging
logging.basicConfig(level=logging.INFO)
DOCS_PATH = "../docs/"


#tt.include_parent()

#tt.get_config()

@task(aliases=["all"])
def generate_all_docs():
    print("Generating all docs (TODO)")
    run("pwd")
    page_settings()

@task(aliases=["sc"])
def take_main_screenshot(path = "screenshots/main-page", output = "/tmp/taskcli-screenshot.svg"):
    tmp_ansi = "/tmp/taskcli-screenshot.ansi"
    with taskcli.utils.change_dir(path):
        run(f"echo '~/project $ t' > {tmp_ansi}")
        run(f"taskcli --color=yes -f tasks.py >> {tmp_ansi}")
        run(f"ansitoimg {tmp_ansi} {output}")
        generator.sanitize_svg(output)
        print(f"Final screenshot: file:///{output}")

@task(aliases=["ps"])
def page_settings():
    page = generator.generate_settings()
    path = "../docs/settings.md"
    generator.write_file(path, page)

    page = generator.generate_example()
    path = "../docs/examples.md"
    generator.write_file(path, page)

    page = generator.generate_advanced_config()
    path = "../docs/advanced_config.md"
    generator.write_file(path, page)





