from taskcli import task, tt


with tt.Group("g1"):
    @task
    def task1():
        print("Hello from task1")