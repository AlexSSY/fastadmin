import uvicorn
from fastapi import FastAPI, Request
import core
import db


app = FastAPI()

settings = {
    'models': [
        'models',
        'dashboard.models'
    ],
}

core.init(app, db.engine, settings)


@app.get('/')
async def home(request: Request):
    return {}


if __name__ == '__main__':
    uvicorn.run("app:app", reload=True)
