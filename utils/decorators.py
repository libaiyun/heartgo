from functools import wraps

from utils.redis import get_redis_connection


def method_lock(lock_key: str = None, expire_time: int = 60, lock_wait=True):
    """
    给方法加redis锁保证分布式环境唯一执行
    用法: @method_lock() 或 method_lock()(your_method)
    :param lock_key: 锁key，默认模块+方法名
    :param expire_time: 锁过期时间（秒）
    :param lock_wait: 是否阻塞式等待锁
    :return:
    """

    def _method_lock(view_func):
        def _wrapped_view(*args, **kwargs):
            func_uniq_key = "lock_{}_{}".format(view_func.__module__.replace(".", "_"), view_func.__name__)
            lock = get_redis_connection().lock(lock_key or func_uniq_key, expire_time, 0.05, 30 * 60)
            if not lock_wait and lock.locked():
                return
            with lock:
                return view_func(*args, **kwargs)

        return wraps(view_func)(_wrapped_view)

    return _method_lock
