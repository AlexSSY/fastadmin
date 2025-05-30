from typing_extensions import Optional


class UniqueValidator:

    def __init__(self, sa_model_class, ):
        self._sa_model_class = sa_model_class

    def __call__(self, *args, **kwargs) -> Optional[str]:
        session_local = kwargs.get("session_local")
        name = kwargs.get("name")
        value = kwargs.get("value")

        if session_local is None or name is None or value is None:
            raise ValueError("UniqueValidator requires 'session_local', 'name', and 'value' in kwargs")
        
        with session_local() as session:
            column = getattr(self._sa_model_class, name)
            record = session.query(
                self._sa_model_class
            ).filter(
                column == value
            ).first()
            
        if record:
            sa_model_name = self._sa_model_class.__name__
            return f"The {name} field already exists in {sa_model_name}"
        
        return None


class RequiredValidator:

    def __call__(self, *args, **kwargs) -> Optional[str]:
        name = kwargs.get("name")
        value = kwargs.get("value")

        if value is None or name is None:
            raise ValueError("RequiredValidator requires 'value', 'name' in kwargs")

        error_message = f"Field {name} required"

        if isinstance(value, str):
            if value is None or value == "":
                return error_message
        elif value is None:
            return error_message

        return None
        

class MaxLengthValidator:

    def __init__(self, max_length):
        self._max_length = max_length

    def __call__(self, *args, **kwargs) -> Optional[str]:
        name = kwargs.get("name")
        value = kwargs.get("value")

        if value is None or name is None:
            raise ValueError("MaxLengthValidator requires 'value', 'name' in kwargs")

        if not isinstance(value, str):
            raise ValueError("The 'value' must be string")
        
        if len(value) > self._max_length:
            return f"Field's length greater than {self._max_length}"
        
        return None
