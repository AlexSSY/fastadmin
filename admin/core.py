import sys
import os
from collections import defaultdict
from importlib import import_module
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from models import ModelAdmin


this = sys.modules[__name__]


# Получаем путь к текущей директории (где находится этот файл)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Указываем путь к папке templates
templates_dir = os.path.join(current_dir, "templates")

_fastapi_app = FastAPI()
_templates = Jinja2Templates(templates_dir)
_engine = None


def get_templating():
    return _templates


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

    '''
    { 'User': SqlalchemyModel }
    '''
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
        _processor = import_module('admin.context_processors').ModelContextProcessor()
        models.append(_processor.get_context(model))
    context['registered_models'] = models

    return context
