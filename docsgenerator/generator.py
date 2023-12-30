from taskcli import task, tt, taskcliconfig


def generate_settings(dest_filepath:str=""):
    config = taskcliconfig.TaskCLIConfig()

    out = """
.. list-table:: Title
   :widths: 25 25 25 25
   :header-rows: 1
"""

    for field in config.get_fields():
        out += f"   * - {field.name}\n"
        out += f"     -  TODO \n"
        out += f"     - {field.desc}\n"

    print(out)

