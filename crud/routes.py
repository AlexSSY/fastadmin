from fastapi import APIRouter, Request


prefix = '/crud'
router = APIRouter(prefix=prefix)


@router.get('/{model}')
def index(request: Request):
    return 'it works'
    

@router.get('/{model}/insert')
def insert(request: Request):
    return 'it works'


@router.post('/{model}/')
def create(request: Request):
    return 'it works'


@router.delete('/{model}/{index}/')
def delete(request: Request):
    return 'it works'


@router.get('/{model}/{index}')
def edit(request: Request):
    return 'it works'


@router.patch('/{model}/{index}/')
def update(request: Request):
    return 'it works'
