from taskcli import task, tt


with tt.Group("g3"):
    @task
    def task3():
        print("Hello from task3")


with tt.Group("g3and5"):
    @task
    def task3shared():
        print("Hello from task3shared")