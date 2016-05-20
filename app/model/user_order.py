from redis_db import client
from constants import USER_ORDER
import hot_redis
from hashlib import md5

class UserOrder:
    def __init__(self, doc=''):
        self.key = md5(doc) ^ md5(USER_ORDER)
        self.users = hot_redis.List(key=self.key, client=client)

    def add(self, user):
        with hot_redis.transaction():
            self.users.add(user)
            self.users.sort()

    def count(self):
        return self.users.count()

    def index(self, user):
        return self.users.index(user)

