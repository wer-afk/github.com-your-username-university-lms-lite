import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("Redis connected successfully")
except Exception:
    redis_client = None
    print("Redis is not available. Using PostgreSQL only.")


def clear_courses_cache():
    if redis_client:
        redis_client.delete("courses_cache")