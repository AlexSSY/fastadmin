import os
from fastapi import Request, Form, Depends
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from .admin import admin
from .forms import SignUpForm
from .depends import get_db, PaginationParams


templates = Jinja2Templates(directory=os.path.join(
    os.path.dirname(__file__), "templates"))


@admin.app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join("admin/static", "favicon.ico"))


@admin.app.get("/signup")
async def sign_up(request: Request):
    form = SignUpForm()
    return templates.TemplateResponse(
        request,
        "signup.html",
        {
            "form": form.get_context(action=f"{admin.prefix}/register")
        }
    )


@admin.app.post("/register")
async def register(
    request: Request,
    username = Form(...),
    password = Form(...),
    password_confirmation = Form(...),
    session = Depends(get_db),
):
    form = SignUpForm(
        username=username,
        password=password,
        password_confirmation=password_confirmation
    )
    form.validate(session)
    return templates.TemplateResponse(
        request,
        "signup.html",
        { "form": form.get_context(action=f"{admin.prefix}/register") }
    )


@admin.app.get("/")
async def dashboard(request: Request):
    pass


@admin.app.get("/{sa_model_name}/index")
async def index(
    request: Request,
    sa_model_name: str,
    pagination: PaginationParams = Depends(),
    session = Depends(get_db)
):
    admin_model_class = admin.get_model_admin_class(sa_model_name)
    
    admin_model_class_instance = admin_model_class()
    fields = admin_model_class.fields
    
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
        "sa_model_classes": admin.registered,
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
