import uuid
from threading import local

_local = local()


class LocalVariable:
    """thread variables enum"""

    USERNAME = "username"


def set_param(key, value):
    """set thread variable"""
    setattr(_local, key, value)


def get_param(key, default=None):
    """get thread variable"""
    return getattr(_local, key, default)


def del_param(key):
    """del thread variable"""
    if hasattr(_local, key):
        delattr(_local, key)


def get_request_username():
    return get_param(LocalVariable.USERNAME, "")


def activate_request(request):
    """
    Generate `request_id` for `request`, then record request to thread `_local`.
    """
    request.request_id = uuid.uuid4().hex
    # 激活body属性, DRF下先访问request.data再访问request.body会出现RawPostDataException
    _ = request.body
    _local.request = request


def get_request():
    """get `request` from current request thread"""
    assert hasattr(_local, "request"), "Can't get_request before activate_request."
    return _local.request


def get_request_id():
    """get `request_id` from current request thread"""
    try:
        return get_request().request_id
    except AttributeError:
        return ""
