import uuid
from threading import local

_local = local()


class LocalVariable:
    """线程变量枚举"""

    USERNAME = "username"


def set_param(key, value):
    """设置线程变量"""
    setattr(_local, key, value)


def get_param(key, default=None):
    """取出线程变量"""
    return getattr(_local, key, default)


def del_param(key):
    """删除线程变量"""
    if hasattr(_local, key):
        delattr(_local, key)


def get_request_username():
    """从线程中取出当前请求用户名"""
    return get_param(LocalVariable.USERNAME, "")


def activate_request(request):
    """
    为request生成请求链id, 并将request存入当前线程中
    """
    request.request_id = uuid.uuid4().hex
    # 激活body属性, DRF下先访问request.data再访问request.body会出现RawPostDataException
    _ = request.body
    _local.request = request


def get_request():
    """取出当前请求线程的request对象"""
    assert hasattr(_local, "request"), "Can't get_request before activate_request."
    return _local.request


def get_request_id():
    """取出当前请求线程的请求链id"""
    try:
        return get_request().request_id
    except AttributeError:
        return ""
