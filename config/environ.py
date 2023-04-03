import os


def get_env_or_raise(key):
    if os.getenv(key) is None:
        raise RuntimeError(
            f'Environment variable "{key}" not found, you must set this variable to run this application.'
        )


APP_CODE = os.getenv("APP_CODE", "heartgo")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

SENTINEL_HOSTS = os.getenv("SENTINEL_HOSTS", "")
SENTINEL_PASSWORD = os.getenv("SENTINEL_PASSWORD")
SENTINEL_SERVICE_NAME = os.getenv("SENTINEL_SERVICE_NAME", "mymaster")
REDIS_MODE = os.getenv("REDIS_MODE", "single").lower()
REDIS_HOSTS = os.getenv("REDIS_HOSTS", "")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = os.getenv("REDIS_DB", 0)
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", 2 ** 10))
REDIS_SOCKET_TIMEOUT = int(os.getenv("REDIS_SOCKET_TIMEOUT", 3))
REDIS_SOCKET_CONNECT_TIMEOUT = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", 5))
REDIS_RETRY_ON_TIMEOUT = os.getenv("REDIS_RETRY_ON_TIMEOUT", "true") == "true"
