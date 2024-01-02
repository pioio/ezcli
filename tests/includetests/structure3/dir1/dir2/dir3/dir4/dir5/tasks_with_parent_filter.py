from taskcli import task, tt
@task
def task3():
    pass

def filterfunc(task):
    return task.name == "task3shared"

tt.config.parent = True
tt.config.parent_task_filter = filterfunc