import json
from collections import OrderedDict

from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from common import logger
from common.local import get_request_id
from common.response import UnifiedJsonResponse


def _format_response_data(data):
    return OrderedDict(
        [
            ("result", True),
            ("code", 0),
            ("message", ""),
            ("permission", None),
            ("request_id", get_request_id()),
            ("data", data),
        ]
    )


class UnifiedResponseMiddleware:
    """统一规范Json响应"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if isinstance(response, UnifiedJsonResponse):
            return response

        if isinstance(response, JsonResponse):
            try:
                data = json.loads(response.content)
                response.content = json.dumps(_format_response_data(data))
                response.status_code = status.HTTP_200_OK
                return response
            except json.decoder.JSONDecodeError:
                logger.exception("统一Json响应格式化失败, 响应数据->%s" % response.content)
                return response

        if isinstance(response, Response):
            response.data = _format_response_data(response.data)
            response.content = response.rendered_content
            response.status_code = status.HTTP_200_OK
            return response

        return response
