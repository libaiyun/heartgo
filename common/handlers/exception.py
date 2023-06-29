import traceback
from collections import OrderedDict

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.views import set_rollback

from common import logger
from common.exceptions import CustomException
from common.local import get_request_id
from common.response import UnifiedJsonResponse


def _format_error(code, message, data=None):
    return OrderedDict(
        [
            ("result", False),
            ("code", code),
            ("message", message),
            ("permission", None),
            ("request_id", get_request_id()),
            ("data", data),
        ]
    )


def exception_handler(exc, context):
    """
    :param exc
    :param context: {"view":None,"args":(),"kwargs":{},"request":None}
    :return:
    """
    request = context["request"]
    request_params = request.GET, request.POST, request.body

    # 项目自定义异常处理
    if isinstance(exc, CustomException):
        logger.log(
            exc.LOG_LEVEL,
            "捕获自定义异常, 错误消息->%s, 错误数据->%s, 其他错误参数->%s, 异常堆栈->%s"
            "请求链id->%s, 请求URL->[%s]%s, 请求参数->%s"
            % (
                str(exc),
                exc.data,
                exc.args,
                traceback.format_exc(),
                get_request_id(),
                request.method,
                request.path,
                request_params,
            ),
        )
        error = _format_error(exc.code, str(exc), exc.data)
        return UnifiedJsonResponse(error)

    # django异常转DRF异常
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    # DRF框架异常处理
    if isinstance(exc, exceptions.APIException):
        logger.warning(
            "捕获DRF框架异常, 错误消息->%s, 异常堆栈->%s"
            "请求链id->%s, 请求URL->[%s]%s, 请求参数->%s"
            % (exc.detail, traceback.format_exc(), get_request_id(), request.method, request.path, request_params)
        )
        headers = {}
        if hasattr(exc, "auth_header"):
            headers["WWW-Authenticate"] = exc.auth_header
        if hasattr(exc, "wait"):
            headers["Retry-After"] = "%d" % exc.wait

        set_rollback()
        error = _format_error(exc.status_code, str(exc.detail))
        return UnifiedJsonResponse(error, headers=headers)

    logger.error(
        "捕获未处理异常，错误消息->%s, 异常堆栈->%s"
        "请求链id->%s, 请求URL->[%s]%s, 请求参数->%s"
        % (exc, traceback.format_exc(), get_request_id(), request.method, request.path, request_params)
    )

    return UnifiedJsonResponse(_format_error(10000, "系统错误, 请联系管理员"))
