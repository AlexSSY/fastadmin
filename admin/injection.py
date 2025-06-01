from . import core


_registry = {}


def register_html_injection(name, fn, priority=100):
    _registry.setdefault(name, []).append((priority, fn))
    _registry[name].sort(key=lambda x: x[0])


def get_html_injections(name, **context):
    injections = _registry.get(name, [])
    return [fn(**context) for _, fn in injections]


def html_injection(name, priority=100):
    def wrapper(fn):
        register_html_injection(name, fn, priority)
        return fn
    return wrapper


def html_class_injection(name, priority=100, *args, **kwargs):
    def wrapper(cls):
        instance = cls(*args, **kwargs)
        register_html_injection(name, instance, priority)
        return cls
    return wrapper


@html_injection('sidebar')
def gunter():
    return '<b>Gunter O. Dim</b>'


@html_class_injection('sidebar')
class Olgierd:
    def __call__(self, *args, **kwds):
        return '<span>Olgierd von Everic</span>'


@html_class_injection('sidebar')
class SidebarUsers:
    def __call__(self, *args, **kwargs):
        return core.get_templating().get_template('partials/_models.html').render(**core.get_context())


if __name__ == '__main__':
    import datetime
    for _ in range(10):
        register_html_injection('sidebar', lambda: f'<div>{datetime.datetime.now()}</div>')

    print(get_html_injections('sidebar'))