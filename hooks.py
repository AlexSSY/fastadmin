_registry = {}


def register_html_hook(name, fn, priority=100):
    _registry.setdefault(name, []).append((priority, fn))
    _registry[name].sort(key=lambda x: x[0])


def get_html_hooks(name, **context):
    hooks = _registry.get(name, [])
    return [fn(**context) for _, fn in hooks]


def html_hook(name, priority=100):
    def wrapper(fn):
        register_html_hook(name, fn, priority)
        return fn
    return wrapper


def html_class_hook(name, priority=100, *args, **kwargs):
    def wrapper(cls):
        instance = cls(*args, **kwargs)
        register_html_hook(name, instance, priority)
        return cls
    return wrapper


@html_hook('sidebar')
def gunter():
    return '<b>Gunter O. Dim</b>'


@html_class_hook('sidebar')
class Olgierd:
    def __call__(self, *args, **kwds):
        return '<span>Olgierd von Everic</span>'


if __name__ == '__main__':
    import datetime
    for _ in range(10):
        register_html_hook('sidebar', lambda: f'<div>{datetime.datetime.now()}</div>')

    print(get_html_hooks('sidebar'))