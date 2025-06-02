from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from ..admin import event


class EmitAccessAttempts(BaseHTTPMiddleware):

    def __init__(self, app, dispatch = None):
        super().__init__(app, dispatch)

    async def dispatch(self, request, call_next):
        # Получаем endpoint-функцию
        endpoint = request.scope.get("endpoint")
        if endpoint:
            func_name = endpoint.__name__
            event_name = f"{func_name}_access"
            event.emit(event_name, request)

        response: Response = await call_next(request)
        return response
