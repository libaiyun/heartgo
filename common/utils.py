import json
import uuid

from django.http import QueryDict

from common import logger
from common.exceptions import ParameterJSONFormatError


def deserialize_request_params(params: QueryDict):
    """
    @param params: https://docs.djangoproject.com/zh-hans/4.0/ref/request-response/#querydict-objects
    @return:
    """
    deserialized_params = {}
    for key, value in dict(params).items():
        if len(value) > 1:
            _value = json.dumps(value)
        else:
            _value = value[0]
        try:
            deserialized_params[key] = json.loads(_value)
        except json.decoder.JSONDecodeError:
            deserialized_params[key] = _value
    return deserialized_params


def get_params_from_request(request):
    """从request中获取请求参数"""
    drf_req_data = getattr(request, "data", {})
    drf_req_params = getattr(request, "query_params", {})
    try:
        request_data = json.loads(request.body or "{}")
    except json.decoder.JSONDecodeError as e:
        logger.exception("请求参数不是正确的JSON格式: %s" % e)
        raise ParameterJSONFormatError
    get_params = deserialize_request_params(request.GET)
    post_params = deserialize_request_params(request.POST)
    return {**get_params, **post_params, **drf_req_params, **request_data, **drf_req_data}


def generate_request_id():
    """生成标识请求线程的id"""
    return uuid.uuid4().hex
