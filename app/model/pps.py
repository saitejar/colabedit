from hashlib import md5
import hot_redis
from redis_db import client
from user_order import UserOrder
from constants import PPS


class PPS:
    def __init__(self, user, doc=''):
        self.key = md5(user) ^ md5(doc) ^ md5(PPS)
        self.pps = hot_redis.Dict(key=self.key, client=client)
        self.users = UserOrder(doc=doc)

    def add(self, pos_stamp, pos_stamp_next, x):
        pass

    def hide(self, pos_stamp):
        pass

    def insert(self, pos, char):
        pass

    def delete(self, pos):
        pass

    def piece(self, pos_stamp_left, pos_stamp_right):
        pass




