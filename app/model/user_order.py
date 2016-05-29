from redis_db import client
from constants import USERS, MAIN_PPS
import hot_redis
from hashlib import md5


class UserOrder:

    def __init__(self, doc=''):
        self.user_key = doc+USERS
        self.users = hot_redis.List(key=self.user_key, client=client)

    def add(self, user):
        with hot_redis.transaction():
            self.users.append(user)
            self.users.sort()
            print self.users, '-----------------------------'

    def remove(self, user):
        self.users.pop(self.users.index(user))
        print self.users

    def count(self):
        return len(self.users)

    def index(self, user):
        return self.users.index(user)


