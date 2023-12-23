def run(cmd):
    BLUE = "\033[94m"
    END = "\033[0m"
    print(f"{BLUE}@@ {cmd}{END}")
    import os
    os.system(cmd)