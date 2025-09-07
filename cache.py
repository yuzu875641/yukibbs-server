import functools
import time
from cachetools import cached, TTLCache

# secondsパラメータを持つデコレーターを定義
# `TTLCache`は指定された秒数だけキャッシュを保持します
def cache(seconds: int = 0):
    cache_instance = TTLCache(maxsize=128, ttl=seconds)

    def decorator(func):
        @functools.wraps(func)
        @cached(cache_instance)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
