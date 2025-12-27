import redis
import os

class RedisAdapter:
    def __init__(self):
        host = os.getenv("REDIS_HOST", "redis")
        port = int(os.getenv("REDIS_PORT", 6380))
        self.r = redis.Redis(host=host, port=port, db=0)

    def exists(self, key):
        return self.r.exists(key)
    
    def set(self, key, value, ex=None):
        self.r.set(key, value, ex=ex)