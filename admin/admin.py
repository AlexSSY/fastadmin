import os
from typing import Any, Callable, Optional
from sqlalchemy import inspect, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.sql.schema import Column
from fastapi import Depends, FastAPI, Request, HTTPException, Form
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from . import helpers
from .validators import RequiredValidator, MaxLengthValidator, UniqueValidator
from .depends import PaginationParams


templates = Jinja2Templates(directory=os.path.join(
    os.path.dirname(__file__), "templates"))

# TODO: сделать авто добавление
templates.env.filters["render_input"] = helpers.render_input
###


class FormField:

    def __init__(
        self,
        name: str,
        type_: str = "string",
        required: bool = False,
        unique: bool = False,
        max: int = 0,
        readonly: bool = False,
        validators: list = None,
        sa_model_class: Optional[Any] = None,
    ):
        self._sa_model_class = sa_model_class
        self.name = name
        self.type_ = type_
        self.required = required
        self. _unique = unique
        self._max = max
        self.readonly = readonly
        self._validators = validators or []

    _default_readonly_columns = ["id"]

    @classmethod
    def from_sa_column(cls, sa_model_class, sa_column: Column):
        validators = []

        if sa_column.nullable is False:
            validators.append(RequiredValidator())

        if isinstance(sa_column.type, String) and sa_column.type.length:
            validators.append(MaxLengthValidator(sa_column.type.length))

        if sa_column.unique:
            validators.append(UniqueValidator(sa_model_class))

        return FormField(
            sa_model_class=sa_model_class,
            name=sa_column.name,
            type_="string",  # Упростим, допустим только строки пока
            required=not sa_column.nullable,
            unique=sa_column.unique or False,
            # max=sa_column.type.length or 0,
            max=0,
            readonly=(sa_column.name in cls._default_readonly_columns),
            validators=validators
        )

    def validate(self, value, session) -> list[str]:
        errors = []
        # TODO рекурсивно запустить валидаторы
        return errors

    def get_context(self):
        return {
            "name": self.name,
            "type_": self.type_
        }


class FieldCollector(type):
    def __new__(cls, name, bases, namespace):
        # Собираем поля из базовых классов
        collected = {}
        for base in bases:
            if hasattr(base, 'fields'):
                collected.update(base.fields)

        # Добавляем поля из текущего класса
        collected.update({
            key: value for key, value in namespace.items()
            if not key.startswith("__") and not callable(value)
        })

        namespace['fields'] = collected
        return super().__new__(cls, name, bases, namespace)


class AdminForm(metaclass=FieldCollector):
    class Meta:
        sa_model_class = None
        submit_text = "Submit"
        template = "partials/_form.html"

    def __init__(self):
        sa_model_class = self.get_sa_model_class()

        if sa_model_class:
            sa_model_class_columns = inspect(sa_model_class).columns

            for sa_column in sa_model_class_columns:
                sa_column_name = sa_column.name
                
                if sa_column_name in self.fields.keys:
                    continue

                self.fields[sa_column_name] = FormField.from_sa_column(
                    self.sa_model_class, sa_column)

    
    def _get_meta(self, attr):
        meta = getattr(self, 'Meta', None)
        if meta:
            return getattr(meta, attr, None)
        return None

    
    def get_sa_model_class(self):
        return self._get_meta('sa_model_class')

    def get_submit_text(self):
        return self._get_meta('submit_text')


    def validate(self, values, session_local):
        pass

    def get_context(self, *, action, method="post"):
        collected_fields_context = []

        for form_field in self.fields.values():
            collected_fields_context.append(form_field.get_context())

        return {
            "action": action,
            "method": method,
            "fields": collected_fields_context,
            "submit_text": self.get_submit_text()
        }

    def save(self, values, session_local):
        new_record = self.sa_model_class(**values)
        with session_local() as session:
            session.add(new_record)
            session.commit()


class AdminModel:
    model: Any

    def __init__(self):
        if getattr(self, "model", None) is None:
            raise ValueError("ModelAdmin requires a 'model' attribute")


        class StandardForm(AdminForm):
            sa_model_class = self.model

        self.form = StandardForm()

    def get_index_fields_names(self) -> list[str]:
        fields = getattr(self, "fields", False)

        if fields and len(fields) > 0:
            return fields

        columns = self._sa_get_columns()
        return [c.name for c in columns]


SqlalchemyUserClass = object


class Admin:

    def __init__(self, app: FastAPI, engine: Engine, secret_key: str):
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
        self._admin_app.add_exception_handler(StarletteHTTPException, admin_http_exception_handler)

        self.register_routes()

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

        class SignUpForm(AdminForm):
            username = FormField(name="username", type_="string")
            password = FormField(name="password", type_="password")
            password_confirmation = FormField(name="password_confirmation", type_="password")

            class Meta:
                submit_text = "Sign Up"
                template = "partials/_form_floating.html"

        self._signup_form_class = SignUpForm

        @self._admin_app.get("/signup")
        def sign_up(request: Request):
            form = self._signup_form_class()
            form_context = form.get_context(action=f"{self._prefix}/register")

            return templates.TemplateResponse(
                request,
                "signup.html",
                { "form": form_context }
            )

        @self._admin_app.post("/register")
        def register(request: Request, username = Form(...), password = Form(...)):
            return {login_field_name: username, password_field_name: password}

    def get_model_admin_class(self, sa_model_name: str) -> AdminModel:
        admin_model_class = self._registered.get(sa_model_name)
        if admin_model_class is None:
            raise HTTPException(status_code=404, detail=f"The {sa_model_name} not found")
        return admin_model_class

    def register_routes(self):
        router = APIRouter()

        def custom(request: Request):
            return dir(request)

        router.get("/custom")(custom)

        @router.get("/")
        def dashboard(request: Request):
            pass

        @router.get("/login")
        def login(request: Request):

            context = {
                "page_title": "Login Page - Admin"
            }
            return templates.TemplateResponse(request, "login.html", context)

        @router.get("/{sa_model_name}/index")
        def index(request: Request, sa_model_name: str, pagination: PaginationParams = Depends()):
            admin_model_class = self.get_model_admin_class(sa_model_name)
            
            admin_model_class_instance = admin_model_class()
            fields = admin_model_class.fields
            
            with self._session_local() as session:
                records = session.query(admin_model_class.model).offset(
                    pagination.offset).limit(pagination.limit).all()
                total_items = session.query(admin_model_class.model).count()
            
            data = []

            for record in records:
                row = []
                for field in fields:
                    if hasattr(admin_model_class_instance, field):
                        _fn = getattr(admin_model_class_instance, field)
                        row.append(_fn(record))
                    else:
                        _val = getattr(record, field)
                        row.append(_val)
                data.append(row)

            def apply_custom_field_names(field):
                custom_field_name_func = getattr(
                    admin_model_class_instance, f"field_{field}_name", None)
                if custom_field_name_func:
                    return custom_field_name_func()
                else:
                    return field

            fields = list(map(apply_custom_field_names, fields))

            per_page = PaginationParams.per_page
            total_pages = (total_items + per_page - 1) // per_page
            start_page = max(1, pagination.page - 2)
            end_page = min(total_pages, pagination.page + 2)

            context = {
                "page_title": f"{sa_model_name} - index",
                "sa_model_classes": self._registered,
                "sa_model_class_name": sa_model_name,
                "fields": fields,
                "data": data,
                "page": pagination.page,
                "per_page": PaginationParams.per_page,
                "total": total_items,
                "total_pages": total_pages,
                "start_page": start_page,
                "end_page": end_page
            }
            return templates.TemplateResponse(request, "index.html", context)
        
        self._admin_app.include_router(router)