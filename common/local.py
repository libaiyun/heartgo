from threading import local

_local = local()


class LocalVariable:
    USERNAME = "username"


def set_thread_var(key, value):
    """设置线程变量"""
    setattr(_local, key, value)


def get_thread_var(key, default=None):
    """获取线程变量"""
    return getattr(_local, key, default)
