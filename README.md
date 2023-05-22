# `taskcli` - a library for utilitarian CLI interfaces


require_env=['FOO']


@task()
@require_env(require_env)
@deps()
def add_no_type(a,b):
    assert isinstance(a, str)
    assert isinstance(b, str)
    log.info (a + b)
    return a + b



# TODO
- make everythin a option. Require @arg for positional args.
- also print env vars in help