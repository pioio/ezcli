from taskcli import task, tt



def test_transitive_includes():
    """Try to import+include modulea, which imports+includes moduleb, which imports+includes modulec.

    In the end we should have 3 tasks, one from each of those modules.
    """
    import os
    print(os.getcwd())

    from tests.transitiveincludes import modulea
    tt.include(modulea)
    tasks = tt.get_tasks()

    task_names = [t.name for t in tasks]
    assert len(tasks) == 3, f"ModuleA has 1 task, ModuleB has 1 task, ModuleC has 1 task. Total 3 tasks. {task_names}"
