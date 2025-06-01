import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from admin import core
from admin.injection import html_injection
from admin.filter import filter_decorator
from admin.event import event_decorator
import db


app = FastAPI()

settings = {
    'models': [
        'models',
    ],
}

core.init(app, db.engine, settings)


@html_injection('head')
def add_favicon():
    return '<script>console.log("head injections");</script>'


@html_injection('sidebar_menu_items')
def add_menu_item():
    return core.get_templating().get_template('partials/_sideitem.html').render()


@filter_decorator('last_menu_item')
def chage_kotia_to_doggy(content):
    return 'doggy'

@filter_decorator('dashboard_header')
def dashboard_header_filter(content):
    return f'<span style="color: red;">{content}</span>'


@filter_decorator('sidebar_model_name')
def sidebar_model_name_uppercase_filter(content):
    return f'<span style="text-transform: uppercase">{content}</span>'


@filter_decorator('sidebar_model_name')
def sidebar_model_name_green_filter(content):
    return f'<span style="color: green;">{content}</span>'


@event_decorator('dashboard_access')
def reject_access(request: Request):
    print('someone just accessing dashboard')
    # raise HTTPException(status_code=401, detail='unauthenticated')


@app.get('/')
async def home(request: Request):
    return {}
