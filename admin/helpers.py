from markupsafe import Markup


def render_input(field, errors=None, values: dict={}):
    """Метод для шаблона Jinja2"""

    name = field.name
    value = values.get(name, "")
    input_type = "text"

    # Пример определения типа поля по SQLAlchemy типу
    # TODO: переработать!!!
    col_type = getattr(field.type, "__class__", type("Text", (), {})).__name__
    if col_type == "Integer":
        input_type = "number"
    elif col_type == "Boolean":
        input_type = "checkbox"
    elif col_type in ("Date", "DateTime"):
        input_type = "date"

    css_class = "form-control"

    if errors and name in errors:
        css_class += " is-invalid"

    html = f'<input class="{css_class}" type="{input_type}" name="{name}" value="{value}">'
    return Markup(html)  # Помечаем как безопасный HTML
