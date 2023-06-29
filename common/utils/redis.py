import functools
import re

from redis import Redis, Sentinel
from redis.cluster import ClusterNode, RedisCluster

from common import logger
from config import environ

_redis_client = None


def _parse_hosts():
    host_pattern = re.compile(r"([\d.\w-]+):(\d+)")
    redis_hosts = host_pattern.findall(environ.REDIS_HOSTS)
    """[('ip', 'port'), ('ip', 'port')]"""
    sentinel_hosts = host_pattern.findall(environ.SENTINEL_HOSTS)
    if not redis_hosts and not sentinel_hosts:
        raise RuntimeError("There is no valid redis or sentinel host, please check the environment variable.")
    return redis_hosts, sentinel_hosts


def _get_connection_kwargs():
    connection_kwargs = {
        # username available when Redis server > 6.0.0
        "username": environ.REDIS_USERNAME,
        "password": environ.REDIS_PASSWORD,
        "db": environ.REDIS_DB,
        "decode_responses": True,
        # default 2**31, perfect if equal to the maximum concurrency on your system.
        "max_connections": environ.REDIS_MAX_CONNECTIONS,
        # Timeout when reading or writing socket after connected,
        # like sending command or read response.
        # Note that it affects other blocking command like blpop, cause early timeout
        # but no effect on lock blocking.
        "socket_timeout": environ.REDIS_SOCKET_TIMEOUT,
        # socket_connect_timeout before we connect
        "socket_connect_timeout": environ.REDIS_SOCKET_CONNECT_TIMEOUT,
        # retry once if socket timeout when connecting or sending command
        "retry_on_timeout": environ.REDIS_RETRY_ON_TIMEOUT,
    }
    return connection_kwargs


def _make_client():
    redis_hosts, sentinel_hosts = _parse_hosts()
    connection_kwargs = _get_connection_kwargs()
    if sentinel_hosts:
        sentinel_kwargs = {"password": environ.SENTINEL_PASSWORD}
        sentinel = Sentinel(sentinel_hosts, sentinel_kwargs=sentinel_kwargs, **connection_kwargs)
        client = sentinel.master_for(environ.SENTINEL_SERVICE_NAME)
    elif len(redis_hosts) > 1:
        connection_kwargs.pop("db", None)
        client = RedisCluster(startup_nodes=[ClusterNode(*host) for host in redis_hosts], **connection_kwargs)
    else:
        client = Redis(*redis_hosts[0], **connection_kwargs)
    return client


class _MakeClient:
    def __init__(self):
        self.redis_hosts, self.sentinel_hosts = _parse_hosts()
        self.connection_kwargs = _get_connection_kwargs()
        self.redis_maker = {
            "single": self._make_single,
            "sentinel": self._make_sentinel,
            "cluster": self._make_cluster,
        }

    def make(self):
        return self.redis_maker.get(environ.REDIS_MODE, self._make_error)()

    def _make_single(self):
        return Redis(*self.redis_hosts[0], **self.connection_kwargs)

    def _make_sentinel(self):
        sentinel_kwargs = {"password": environ.SENTINEL_PASSWORD}
        sentinel = Sentinel(self.sentinel_hosts, sentinel_kwargs=sentinel_kwargs, **self.connection_kwargs)
        return sentinel.master_for(environ.SENTINEL_SERVICE_NAME)

    def _make_cluster(self):
        self.connection_kwargs.pop("db", None)
        return RedisCluster(startup_nodes=[ClusterNode(*host) for host in self.redis_hosts], **self.connection_kwargs)

    def _make_error(self):
        raise RuntimeError(
            "REDIS_MODE not supported: '{}', options: {}".format(environ.REDIS_MODE, list(self.redis_maker))
        )


def get_redis_client():
    global _redis_client
    if not _redis_client:
        _redis_client = _make_client()
    return _redis_client


def redis_lock(key=None, expire=60, lock_wait=True, sleep=0.05, blocking_timeout=30 * 60):
    """
    redis实现分布式锁
    :param key: 锁key
    :param expire: 锁过期时间
    :param lock_wait: 是否阻塞等待锁
    :param sleep: 锁阻塞时, 尝试循环获取锁的间隔时间
    :param blocking_timeout: 锁阻塞等待的最大时间
    :return:
    """

    def wrapper(func):
        def decorated(*args, **kwargs):
            if key is None:
                name = "locked_{}_{}".format(func.__module__, func.__qualname__)
            else:
                name = key
            lock = get_redis_client().lock(name, expire, sleep, blocking_timeout=blocking_timeout)
            if not lock_wait and lock.locked():
                logger.error("检查到redis锁，代码执行提前结束, 锁key->%s" % name)
                return
            with lock:
                return func(*args, **kwargs)

        return functools.wraps(func)(decorated)

    return wrapper
