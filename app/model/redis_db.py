from hot_redis import HotClient
import redis

client = HotClient(host="localhost", port=6379)

redis_manager = redis.Redis(host="localhost", port=6379)

