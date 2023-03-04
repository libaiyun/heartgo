import os


def get_env_or_raise(key):
    if os.getenv(key) is None:
        raise RuntimeError(
            f'Environment variable "{key}" not found, you must set this variable to run this application.'
        )


APP_CODE = os.getenv("APP_CODE", "heartgo")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
REDIS_HOSTS = os.getenv("REDIS_HOSTS", "")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = os.getenv("REDIS_DB", 0)
SENTINEL_HOSTS = os.getenv("SENTINEL_HOSTS", "")
SENTINEL_SERVICE_NAME = os.getenv("SENTINEL_SERVICE_NAME", "")
