from redis_db import client
from constants import USERS, MAIN_PPS
import hot_redis


class UserOrder:

    def __init__(self, doc=''):
        self.user_key = doc + USERS
        self.users = hot_redis.Dict(key=self.user_key, client=client)
        self.id = hot_redis.Int(key=self.user_key+"ID", client=client)
        self.changes = hot_redis.Dict(key=self.user_key+"changes", client=client)

    def add(self, user):
        with hot_redis.transaction():
            numberOfUsers = len(self.users.items())
            self.users[user.lower()] = numberOfUsers

    def remove(self, user):
        self.users.pop(self.users.index(user))
        print self.users

    def count(self):
        return len(self.users)

    def index(self, user):
        if user in self.users.keys():
            return self.users[user]
        else:
            return -1

    def get_change_id(self):
        with hot_redis.transaction():
            id = self.id.value
            self.id.value = id+1
            return self.id.value




