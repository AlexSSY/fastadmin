class Indexable:
    
    def index(self, request):
        pass


class UserAuthorization:

    def can_index(self, request):
        return request.admin.user.role == "admin"
    
    def can_everything(self, request):
        return request.admin.user.role == "admin"


class FormField:
    
    def __init__(self, name, type_):
        self.name = name
        self.type_ = type_

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

    def get_sa_model_class(self):
        # Получаем значение из Meta, если есть
        meta = getattr(self, 'Meta', None)
        if meta and hasattr(meta, 'sa_model_class'):
            return meta.sa_model_class
        return None

    def get_context(self, *, action, method="post"):
        collected_fields_context = []

        for form_field in self.fields.values():
            collected_fields_context.append(form_field.get_context())

        return {
            "action": action,
            "method": method,
            "fields": collected_fields_context
        }


class LoginForm(AdminForm):
    username = FormField(name="Username", type_="string")
    password = FormField(name="password", type_="password")


lf = LoginForm()
print(lf.get_context(action="/register"))
