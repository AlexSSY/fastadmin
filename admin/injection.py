from . import event
from markupsafe import Markup


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


def render_injections(slot_name, **context):
    """Возвращает объединённый HTML, инжектированный в указанный слот."""
    blocks = get_html_injections(slot_name, **context)
    return Markup("\n".join(blocks))


def set_env_to_templates(templates):
    templates.env.globals["render_injections"] = render_injections


event.on('templates_initialized', set_env_to_templates)
