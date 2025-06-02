import sys
import os
from importlib import import_module
from importlib.util import find_spec
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from . import event
from .bases import ModelAdmin


this = sys.modules[__name__]


# Получаем путь к текущей директории (где находится этот файл)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Указываем путь к папке templates
templates_dir = os.path.join(current_dir, "templates")

_fastapi_app = FastAPI()
_templates = None
_engine = None
_registered_models = {}


def get_templating():
    return _templates


def _load_specific_type_objects_from_module(module, subclass_, type_=type):
    for name, class_ in module.__dict__.items():
        if not isinstance(class_, type_) or class_.__module__ != module.__name__:
            continue
        if issubclass(class_, subclass_):
           yield  name, class_


def _load_models(module):
    for name, class_ in _load_specific_type_objects_from_module(module, ModelAdmin):
        _registered_models[name] = class_


def _load_middlewares(module):
    from starlette.middleware.base import BaseHTTPMiddleware
    for name, class_ in _load_specific_type_objects_from_module(module, BaseHTTPMiddleware):
        _fastapi_app.add_middleware(class_)


def get_registered_models():
    return getattr(this, '_registered_models', {})


def _load_module(package, module):
    try:
        return import_module(f'{package}.{module}')
    except ModuleNotFoundError:
        return None
    except ImportError:
        return None


def _load_plugins(plugins_list):
    templates_path_list = []

    for plugin_module_name in plugins_list:
        # Импортируем модуль
        plugin_module = import_module(plugin_module_name)

        # Получаем путь к модулю через find_spec
        spec = find_spec(plugin_module_name)
        if spec and spec.origin:
            module_path = os.path.dirname(os.path.abspath(spec.origin))
            templates_path_list.append(os.path.join(module_path, "templates"))

        # Загрузка моделей, если есть
        models_module = _load_module(plugin_module_name, 'models')
        if models_module:
            _load_models(models_module)

        # Middleware loading if present
        middlewares_module = _load_module(plugin_module_name, 'middlewares')
        if middlewares_module:
            _load_middlewares(middlewares_module)

        # routes loading if present
        routes_module = _load_module(plugin_module_name, 'routes')
        if routes_module:
            router = getattr(routes_module, 'router', False)
            if router:
                get_fastapi_application().include_router(router)

    # Добавляем основной каталог шаблонов
    templates_path_list.append(templates_dir)

    global _templates
    _templates = Jinja2Templates(directory=templates_path_list)

    event.emit('templates_initialized', _templates)


def init(app, engine, settings):
    app.mount('/admin', _fastapi_app, 'admin-app')
    global _engine
    _engine = engine
    _load_plugins(settings.get('plugins', []))


def get_fastapi_application():
    return _fastapi_app

