from sqlalchemy import inspect

from .fields import FormField, EmailField, PasswordField


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

    def __init__(self, **form_data):
        sa_model_class = self.get_sa_model_class()

        if sa_model_class:
            sa_model_class_columns = inspect(sa_model_class).columns

            for sa_column in sa_model_class_columns:
                sa_column_name = sa_column.name
                
                if sa_column_name in self.fields.keys:
                    continue

                self.fields[sa_column_name] = FormField.from_sa_column(
                    self.sa_model_class, sa_column)
                
        for key, val in form_data.items():
            self.fields[key].value = val

    
    def _get_meta(self, attr):
        meta = getattr(self, 'Meta', None)
        if meta:
            return getattr(meta, attr, None)
        return None
    
    def get_sa_model_class(self):
        return self._get_meta('sa_model_class')

    def get_submit_text(self):
        return self._get_meta('submit_text')

    def validate(self, session_local):
        for form_field in self.fields.values():
            form_field.clear_errors()
            form_field.validate(form_field.value, session_local)

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


class SignUpForm(AdminForm):
    username = EmailField(name="username", required=True)
    password = PasswordField(name="password", required=True)
    password_confirmation = PasswordField(name="password_confirmation")

    def validate(self, session_local):
        super().validate(session_local)
        password = self.fields["password"]
        password_confirmation = self.fields["password_confirmation"]
        if password != password_confirmation:
            self.password_confirmation.add_error("Пароли не совпадают")

    class Meta:
        submit_text = "Sign up"
        template = "partials/_form_floating.html"
