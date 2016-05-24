from redis_db import client
from constants import USERS
import hot_redis
from hashlib import md5
from constants import CURSOR_POS, CURSOR_COLOR


class UserOrder:

    def __init__(self, doc=''):
        self.user_key = md5(doc+USERS)
        self.user_cursor_pos_key = md5(doc+CURSOR_POS)
        self.user_cursor_color_key = md5(doc+CURSOR_COLOR)
        self.users = hot_redis.List(key=self.user_key, client=client)
        self.user_cursor_pos = hot_redis.Dict(key=self.user_cursor_pos_key, client=client)
        self.user_cursor_color = hot_redis.Dict(key=self.user_cursor_color_key, client=client)

    def add(self, user):
        with hot_redis.transaction():
            self.users.append(user)
            self.users.sort()
        print self.users

    def count(self):
        return len(self.users)

    def index(self, user):
        return self.users.index(user)
