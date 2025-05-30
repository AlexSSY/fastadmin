from typing import Any, Optional
from sqlalchemy import String
from sqlalchemy.schema import Column

from .validators import (
    MaxLengthValidator,
    RequiredValidator,
    UniqueValidator
)


class FormField:

    def __init__(
        self,
        *,
        name: str,
        type_: str = "string",
        value: Any = None,
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
        self.value = value
        self.required = required
        self. _unique = unique
        self._max = max
        self.readonly = readonly

        dynamic_validators_list = []

        if required:
            dynamic_validators_list.append(RequiredValidator())

        self._validators = validators or dynamic_validators_list
        self._errors = []

    _default_readonly_columns = ["id"]

    def __eq__(self, value):
        return self.value == value.value

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
    
    def add_error(self, error):
        self._errors.append(error)

    def get_errors(self):
        return self._errors
    
    def clear_errors(self):
        self._errors.clear()

    def validate(self, value, session):
        for validator in self._validators:
            result = validator(name=self.name, value=value)
            if result:
                self._errors.append(result)

    def get_context(self):
        return {
            "name": self.name,
            "type_": self.type_,
            "value": self.value or "",
            "errors": self._errors,
            "required": self.required,
        }
    

class EmailField(FormField):

    def __init__(self, *, name, type_ = "email", value = None, required = False, 
                 unique = False, max = 0, readonly = False, validators = None, 
                 sa_model_class = None):
        super().__init__(name=name, type_=type_, value=value, required=required, 
                         unique=unique, max=max, readonly=readonly, 
                         validators=validators, sa_model_class=sa_model_class)
                        

class PasswordField(FormField):

    def __init__(self, *, name, type_ = "password", value = None, required = False, 
                 unique = False, max = 0, readonly = False, validators = None, 
                 sa_model_class = None):
        super().__init__(name=name, type_=type_, value=value, required=required, 
                         unique=unique, max=max, readonly=readonly, 
                         validators=validators, sa_model_class=sa_model_class)
        
    def get_context(self):
        context = super().get_context()
        context["value"] = ""
        return context