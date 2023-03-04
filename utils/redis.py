import re

from redis import Redis, Sentinel
from redis.cluster import ClusterNode, RedisCluster

from config import environ

redis_connection = None


def get_redis_connection():
    global redis_connection
    if redis_connection:
        return redis_connection

    host_pattern = re.compile(r"([\d.\w-]+):(\d+)")
    redis_hosts = host_pattern.findall(environ.REDIS_HOSTS)
    """[('ip', 'port'), ('ip', 'port')]"""
    sentinel_hosts = host_pattern.findall(environ.SENTINEL_HOSTS)
    if not redis_hosts and not sentinel_hosts:
        raise RuntimeError("There is no valid redis or sentinel host, please check the environment variable.")

    connection_kwargs = {
        "password": environ.REDIS_PASSWORD,
        "db": environ.REDIS_DB,
    }

    if sentinel_hosts:
        sentinel = Sentinel(sentinel_hosts, **connection_kwargs)
        redis_connection = sentinel.master_for(environ.SENTINEL_SERVICE_NAME)
    elif len(redis_hosts) > 1:
        connection_kwargs.pop("db")
        redis_connection = RedisCluster(startup_nodes=[ClusterNode(*host) for host in redis_hosts], **connection_kwargs)
    else:
        redis_connection = Redis(*redis_hosts[0], **connection_kwargs)

    return redis_connection
