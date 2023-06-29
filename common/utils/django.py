import json

from django.http import QueryDict
from django.urls import get_resolver, set_urlconf

from common import logger
from common.exceptions import ParamFormatError


def resolve_request(request):
    """
    从request请求对象中解析视图处理函数和函数入参,
    借鉴 django.core.handlers.base.BaseHandler.resolve_request
    """
    if hasattr(request, "urlconf"):
        urlconf = request.urlconf
        set_urlconf(urlconf)
        resolver = get_resolver(urlconf)
    else:
        resolver = get_resolver()
    resolver_match = resolver.resolve(request.path_info)
    view_func, view_args, view_kwargs = resolver_match
    return view_func, view_args, view_kwargs


def _deserialize_request_params(request_params) -> dict:
    """
    反序列化 QueryDict 类型的请求参数, 转换成字典
    参考: https://docs.djangoproject.com/zh-hans/4.0/ref/request-response/#querydict-objects
    示例:
        请求参数: QueryDict('a=1&a=2&c=3&d=[1,2]&e={"x":1}')
        返回值: {'a': ['1', '2'], 'c': 3, 'd': [1, 2], 'e': {'x': 1}}
    :param request_params: 请求参数request.GET/POST/query_params
    :return: 反序列化后的请求参数字典
    """
    if not isinstance(request_params, QueryDict):
        return request_params

    params = dict()
    for key, value in dict(request_params).items():
        if len(value) > 1:
            _value = json.dumps(value)
        else:
            _value = value[0]
        try:
            params[key] = json.loads(_value)
        except (json.decoder.JSONDecodeError, TypeError):
            params[key] = _value

    return params


def get_params_from_request(request, raise_exception=True):
    """从request请求对象中读取所有请求参数, 并反序列化为字典"""
    get_params = _deserialize_request_params(request.GET)
    post_params = _deserialize_request_params(request.POST)

    data = dict()
    if hasattr(request, "data"):
        # request.data 可能是 QueryDict
        data = _deserialize_request_params(request.data)
    elif request.content_type == "application/json":
        try:
            data = json.loads(request.body or "{}")
        except json.decoder.JSONDecodeError:
            if raise_exception:
                raise ParamFormatError("请求参数不是正确的JSON格式", request.body)
            logger.exception("请求参数不是正确的JSON格式, 请求体->%s" % request.body)

    return dict(**get_params, **post_params, **data)
