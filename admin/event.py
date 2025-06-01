_listeners = {}


def on(event_name, handler):
        _listeners.setdefault(event_name, []).append(handler)


def emit( event_name, *args, **kwargs):
    if event_name != "event_emitted":
        emit("event_emitted", name=event_name, args=args, kwargs=kwargs)
    
    for handler in _listeners.get(event_name, []):
        handler(*args, **kwargs)


def event_decorator(event_name):
    def wrapper(fn):
        on(event_name, fn)
        return fn
    return wrapper