import uuid

from django.utils.deprecation import MiddlewareMixin

from common import local


class CommonMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.request_id = uuid.uuid4().hex
        username = getattr(request.user, "username")
        local.set_thread_var(local.LocalVariable.USERNAME, username)
