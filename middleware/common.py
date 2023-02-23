import uuid

from django.utils.deprecation import MiddlewareMixin

from common import local


def _record_request_to_thread(request):
    """将请求信息记录到线程变量"""
    request.request_id = uuid.uuid4().hex
    username = getattr(request.user, "username")
    local.set_thread_var(local.LocalVariable.USERNAME, username)


class CommonMiddleware(MiddlewareMixin):
    """公共中间件"""

    def process_request(self, request):
        _record_request_to_thread(request)
