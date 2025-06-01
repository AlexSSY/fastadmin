import uvicorn
from fastapi import FastAPI, Request
from admin import core
import db


app = FastAPI()

settings = {
    'models': [
        'models',
    ],
}

core.init(app, db.engine, settings)


@app.get('/')
async def home(request: Request):
    return {}


if __name__ == '__main__':
    # db.Base.metadata.create_all(bind=db.engine)
    uvicorn.run("app:app", reload=True)
