_filters = {}


def add_filter(name, fn, priority=100):
    _filters.setdefault(name, []).append((priority, fn))
    _filters[name].sort(key=lambda item: item[0])


def apply_filter(name, value, *args, **kwargs):
    for _, fn in _filters.get(name, []):
        value = fn(value, *args, **kwargs)
    return value