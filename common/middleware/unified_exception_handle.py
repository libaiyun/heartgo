from common.handlers.exception import exception_handler
from common.utils.django import resolve_request


class ExceptionHandleMiddleware:
    """统一异常处理"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        view_func, view_args, view_kwargs = resolve_request(request)
        context = {"view": view_func, "args": view_args, "kwargs": view_kwargs, "request": request}
        response = exception_handler(exception, context)
        return response
