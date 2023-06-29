from django.http import JsonResponse

from common.utils.json import CustomJSONEncoder


class CustomJsonResponse(JsonResponse):
    """自定义encoder的JsonResponse"""

    def __init__(self, data, encoder=CustomJSONEncoder, **kwargs):
        super().__init__(data, encoder=encoder, **kwargs)


class UnifiedJsonResponse(CustomJsonResponse):
    """
    统一Json响应
    data需符合以下规范：
    result (bool) 请求成功与否。true请求成功；false请求失败
    code (int) 错误编码。 0表示success，>0表示失败错误
    message (string) 请求失败返回的错误信息
    permission (object) 权限信息
    request_id (string) 请求链id
    data (object) 请求返回的数据
    """

    pass
