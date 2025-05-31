from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates()


@router.get('/dashboard')
def dashboard(request: Request):
    return