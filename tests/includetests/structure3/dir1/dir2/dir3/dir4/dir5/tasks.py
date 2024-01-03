from taskcli import task, tt

tt.include_parent()

with tt.Group("g5"):
    @task
    def task5():
        print("Hello from task5")

with tt.Group("g3and5"): # same name as in dir3
    @task
    def task5shared():
        print("Hello from task5shared")