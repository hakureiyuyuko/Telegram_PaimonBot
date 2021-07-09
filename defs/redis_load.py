from configparser import RawConfigParser
from os import getcwd, sep
from redis import StrictRedis
from redis.exceptions import RedisError


def get_redis_conf():
    config = RawConfigParser()
    config.read(f"{getcwd()}{sep}config.ini")
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    redis_host = config.get("redis", "host", fallback=redis_host)
    redis_port = config.get("redis", "port", fallback=redis_port)
    redis_db = config.get("redis", "db", fallback=redis_db)
    return {'host': redis_host, 'port': redis_port, 'db': redis_db}


redis = StrictRedis(host=get_redis_conf()['host'],
                    port=get_redis_conf()['port'],
                    db=get_redis_conf()['db'])


def redis_status():
    try:
        redis.ping()
        return True
    except RedisError:
        return False
