import sys
from collections import defaultdict
from importlib import import_module
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from models import ModelAdmin


this = sys.modules[__name__]


_fastapi_app = FastAPI()
_templates = Jinja2Templates('templates')
_engine = None


_hooks = defaultdict(list)


def register_html_hook(name, fn):
    _hooks.setdefault(name, []).append(fn)


def _load_models(models_list):
    registered_models = {}
    for module_name in models_list:
        module = import_module(module_name)
        # registered_models.update(dict({n: c for n, c in module.__dict__.items() if issubclass(c, ModelAdmin)}))
        for name, class_ in module.__dict__.items():
            if not isinstance(class_, type) or class_.__module__ != module.__name__:
                continue
            if issubclass(class_, ModelAdmin):
                registered_models[name] = class_

    setattr(this, '_registered_models', registered_models)


def get_registered_models():
    return getattr(this, '_registered_models', {})


def init(app, engine, settings):
    app.mount('/admin', _fastapi_app, 'admin-app')
    _engine = engine
    _load_models(settings['models'])


def get_fastapi_application():
    return _fastapi_app


def get_context():
    context = {}

    # models
    models = []
    for model in get_registered_models().values():
        _processor = import_module('context_processors').ModelContextProcessor()
        models.append(_processor.get_context(model))
    context['registered_models'] = models

    return context

@_fastapi_app.get('/')
def dashboard(request: Request):

    # я в dashboard endpoint мне ну-жен {model}_dashboard_ContextProcessor
    return _templates.TemplateResponse(request, "dashboard.html", get_context())


@_fastapi_app.get('/{model}')
def index(request: Request):
    ...
    # я в index endpoint мне нужны [index]