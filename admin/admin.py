import os
from typing import Any, Callable
from sqlalchemy import inspect, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.sql.schema import Column
from fastapi import Depends, FastAPI, Request
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from . import helpers
from .validators import RequiredValidator, MaxLengthValidator, UniqueValidator
from .depends import PaginationParams


templates = Jinja2Templates(directory=os.path.join(
    os.path.dirname(__file__), "templates"))

# TODO: сделать авто добавление
templates.env.filters["render_input"] = helpers.render_input
###


class Field:

    def __init__(
        self,
        sa_model_class: Any,
        name: str,
        type_: str = "string",
        required: bool = False,
        unique: bool = False,
        max: int = 0,
        readonly: bool = False,
        validators: list = None
    ):
        self._sa_model_class = sa_model_class
        self.name = name
        self._type = type_
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

        return Field(
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

    _valid_types = ["string", "integer"]

    @property
    def type_(self):
        return self._type

    @type_.setter
    def type_(self, value: str) -> str:
        _value = value.lower()
        if _value not in Field._valid_types:
            raise ValueError("Invalid type for field")
        self._type = _value

    def __str__(self):
        return self.name


class Form:
    sa_model_class = None

    def __init__(self):
        if not getattr(self, "sa_model_class", None):
            raise ValueError("Form requires sa_model_class")

        # сгенерируем Fields
        sa_model_class_columns = inspect(self.sa_model_class).columns

        self._fields = []

        for sa_column in sa_model_class_columns:
            self._fields.append(Field.from_sa_column(
                self.sa_model_class, sa_column))

    def validate(self, values, session_local):
        pass

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


        class StandardForm(Form):
            sa_model_class = self.model

        self.form = StandardForm()

    def get_index_fields_names(self) -> list[str]:
        fields = getattr(self, "fields", False)

        if fields and len(fields) > 0:
            return fields

        columns = self._sa_get_columns()
        return [c.name for c in columns]


class Admin:

    def __init__(self, app: FastAPI, engine: Engine, current_user_dependency: Callable = None):
        self._app = app
        self._engine = engine
        self._current_user_dependency = current_user_dependency
        self._registered = {}
        self._prefix = "/admin"
        self._session_local = sessionmaker(
            bind=engine, autoflush=False, autocommit=False)

        self.register_routes()

    def register(self, sa_model_class, admin_model_class: AdminModel):
        self._registered[sa_model_class.__name__] = admin_model_class

    def provide_authentication_details(
        self,
        sa_user_model,
        login_field_name,
        password_field_name,
        password_verify_callback
    ):
        self._sa_user_model = sa_user_model

    def register_routes(self):
        router = APIRouter(prefix=self._prefix)

        @router.get("/")
        def dashboard(request: Request, current_user=Depends(self._current_user_dependency)):
            pass

        @router.get("/login")
        def login(request: Request):

            context = {
                "page_title": "Login Page - Admin"
            }
            return templates.TemplateResponse(request, "login.html", context)

        @router.get("/{sa_model_name}/index")
        def index(request: Request, sa_model_name: str, pagination: PaginationParams = Depends()):
            admin_model_class = self._registered[sa_model_name]
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
        
        self._app.include_router(router)