from fastapi import Request
from .core import get_fastapi_application, get_templating, get_context
from .event import emit


app = get_fastapi_application()


@app.get('/')
def dashboard(request: Request):
    emit('dashboard_access', request)
    return get_templating().TemplateResponse(request, "dashboard.html", get_context())


@app.get('/{model}')
def index(request: Request):
    ...
    

@app.get('/{model}/insert')
def insert(request: Request):
    ...


@app.post('/{model}/')
def create(request: Request):
    ...


@app.delete('/{model}/{index}/')
def delete(request: Request):
    ...


@app.get('/{model}/{index}')
def edit(request: Request):
    ...


@app.patch('/{model}/{index}/')
def update(request: Request):
    ...
