def task(func):
    def wrapper():
        print("Before decorator")
        func()
        print("After decorator")

    return wrapper


def somefunction():
    print("This is some function")
