import os
from typing import Any, Callable
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware


templates = Jinja2Templates(directory=os.path.join(
    os.path.dirname(__file__), "templates"))

# TODO: сделать авто добавление
# templates.env.filters["render_input"] = helpers.render_input
###

class AdminModel:
    model: Any

    def __init__(self):
        if getattr(self, "model", None) is None:
            raise ValueError("ModelAdmin requires a 'model' attribute")

    def get_index_fields_names(self) -> list[str]:
        fields = getattr(self, "fields", False)

        if fields and len(fields) > 0:
            return fields

        columns = self._sa_get_columns()
        return [c.name for c in columns]


SqlalchemyUserClass = object


class Admin:

    def init(self, app: FastAPI, engine: Engine, secret_key: str):
        self._app = app
        self._engine = engine
        self._secret_key = secret_key
        self._registered = {}
        self._prefix = "/admin"
        self._session_local = sessionmaker(
            bind=engine, autoflush=False, autocommit=False)
        self._admin_app = FastAPI()
        self._app.mount("/admin", self._admin_app)

        async def admin_http_exception_handler(request: Request, exc: StarletteHTTPException):
            if exc.status_code == 404:
                return templates.TemplateResponse(
                    "404.html", {"request": request, "detail": exc.detail}, status_code=404
                )
            if exc.status_code == 401:
                return templates.TemplateResponse(
                    "404.html", {"request": request, "detail": exc.detail}, status_code=404
                )

        self._admin_app.add_exception_handler(StarletteHTTPException, admin_http_exception_handler)

    
    @property
    def app(self):
        return self._admin_app
    
    @property
    def prefix(self):
        return self._prefix
    
    @property
    def session_local(self):
        return self._session_local
    
    @property
    def registered(self):
        return self._registered

    async def get_db(self):
        db = self._session_local()
        try:
            yield db
        finally:
            db.close()

    def register(self, sa_model_class, admin_model_class: AdminModel):
        self._registered[sa_model_class.__name__] = admin_model_class

    def provide_authentication_details(
        self,
        sa_user_class: SqlalchemyUserClass,
        login_field_name: str,
        password_field_name: str,
        password_verify_callback: Callable
    ):
        self.sa_user_class = sa_user_class
        self._login_field_name = login_field_name
        self._password_field_name = password_field_name
        self.password_verify_callback = password_verify_callback

        self._admin_app.add_middleware(SessionMiddleware, secret_key=self._secret_key)

    def get_model_admin_class(self, sa_model_name: str) -> AdminModel:
        admin_model_class = self._registered.get(sa_model_name)
        if admin_model_class is None:
            raise HTTPException(status_code=404, detail=f"The {sa_model_name} not found")
        return admin_model_class


admin = Admin()