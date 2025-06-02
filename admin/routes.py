from fastapi import Request
from .core import get_fastapi_application
from .event import emit
from .views import DashboardView


app = get_fastapi_application()


@app.get('/')
def dashboard(request: Request):
    return DashboardView().get_response()
