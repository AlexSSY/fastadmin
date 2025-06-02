from . import event
from markupsafe import Markup


_filters = {}


def add_filter(name, fn, priority=100):
    _filters.setdefault(name, []).append((priority, fn))
    _filters[name].sort(key=lambda item: item[0])


def filter_decorator(name, priority=100):
    def wrapper(fn):
        add_filter(name, fn, priority)
        return fn
    return wrapper


def apply_filter(name, value, *args, **kwargs):
    for _, fn in _filters.get(name, []):
        value = fn(value, *args, **kwargs)
    return value


def apply_all_filters(name, value, *args, **kwargs):
    for _, fn in _filters.get(name, []):
        value = fn(value, *args, **kwargs)
    return Markup(value)


def jinja_apply_filter(value, filter_name, *args, **kwargs):
    return apply_all_filters(filter_name, value, *args, **kwargs)


def set_env_to_templates(templates):
    templates.env.filters["apply_filters"] = jinja_apply_filter


event.on('templates_initialized', set_env_to_templates)
