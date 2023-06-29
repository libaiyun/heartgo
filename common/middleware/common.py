from django.http import HttpResponseBase
from django.utils.deprecation import MiddlewareMixin

from common import local
from common.local import get_request_id


class CommonMiddleware(MiddlewareMixin):
    """
    公共中间件
    中间件前置, 保证后续中间件拿到线程中的request相关变量, 保证对最终的response修改headers生效。
    """

    def process_request(self, request):
        username = getattr(request.user, "username", "")
        local.set_param(local.LocalVariable.USERNAME, username)

        local.activate_request(request)

    def process_response(self, request, response):
        if isinstance(response, HttpResponseBase):
            response.headers["X-Request-Id"] = get_request_id()
        return response
