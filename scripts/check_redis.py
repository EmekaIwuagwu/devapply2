import redis
import sys

try:
    r = redis.from_url("redis://localhost:6379")
    r.ping()
    print("SUCCESS: Redis is running.")
except Exception as e:
    print(f"FAILED: Redis is not running. {e}")
    sys.exit(1)
