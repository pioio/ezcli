# `taskcli` - a library for utilitarian CLI interfaces

taskcli.default_env = {

}



@task(require_env=[FOO])
def add_no_type(a,b):
    assert isinstance(a, str)
    assert isinstance(b, str)
    log.info (a + b)
    return a + b
