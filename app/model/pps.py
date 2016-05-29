from hashlib import md5
import hot_redis
from redis_db import client
from redis_db import redis_manager
from user_order import UserOrder
from constants import PPS_STRUCT, POS_TAGS, KEYS, PERSIST, YES, NO, PHI, MAIN_PPS


class PPS:
    def __init__(self, user='', doc=''):
        self.key = md5(str(MAIN_PPS) + doc + PPS_STRUCT).hexdigest()
        self.key_pos_tags = md5(str(MAIN_PPS) + doc + POS_TAGS).hexdigest()
        self.key_map_persistent = md5(str(MAIN_PPS) + doc + PERSIST).hexdigest()
        self.pps = hot_redis.Dict(key=self.key, client=client)
        self.tags = hot_redis.List(key=self.key_pos_tags, client=client)
        self.persist = hot_redis.Dict(key=self.key_map_persistent, client=client)
        self.user_list = UserOrder(doc=doc)
        self.user = user
        if hot_redis.List(key=KEYS, client=client).count(self.key) == 0:
            self.pps['0'] = PHI  # unicode for null
            self.pps['1'] = PHI  # unicode for null
            self.persist['0'] = YES
            self.persist['1'] = YES
            self.tags.append('0')
            self.tags.append('1')
            hot_redis.List(key=KEYS, client=client).append(self.key)

    def add(self, pos_stamp, pos_stamp_next, x):
        with hot_redis.transaction():
            x = chr(x)
            pos_stamp = float(pos_stamp)
            pos_stamp_next = float(pos_stamp_next)
            pos = pos_stamp + (pos_stamp_next - pos_stamp) / 2

            self.pps[str(pos)] = x
            self.tags.append(str(pos))
            self.tags.sort()  # optimize
            self.persist[str(pos)] = YES

    def hide(self, pos_stamp):
        if str(pos_stamp) in self.pps:
            self.pps[str(pos_stamp)] = 0
            self.persist[str(pos_stamp)] = NO

    def insert(self, ch, pos):
        print self.user
        print self.user_list.users
        index = self.user_list.users.index(self.user)
        pos = int(pos)
        no_of_users = len(self.user_list.users)
        print 'no of users === ', no_of_users
        lower_bound = 0
        lower_bound_persist = 0
        upper_bound_persist = 0
        found = False
        with hot_redis.transaction():
            self.tags.sort()
            for tag in self.tags:
                if self.pps[tag] != PHI:
                    lower_bound += 1
                if lower_bound == pos:
                    found = True
                    break

            print self.tags
            ltag = self.tags[lower_bound]
            rtag = self.tags[lower_bound + 1]
            if self.persist[ltag] == YES and self.persist[rtag] == YES:
                print ltag, rtag, ' = YY'
                left = float(ltag)
                right = float(rtag)
            elif self.persist[ltag] == NO and self.persist[rtag] == NO:
                left = float(ltag)
                right = float(rtag)
            elif self.persist[ltag] == NO and self.persist[rtag] == YES:
                for p in range(lower_bound - 1, -1, -1):
                    if self.persist[self.tags[p]] == YES:
                        lower_bound_persist = str(p)
                        break
                left = float(ltag)
                lower_bound_persist = float(self.tags[lower_bound_persist])
                right = lower_bound_persist + (index + 1) * (
                    float(rtag) - lower_bound_persist) / no_of_users
            else:
                for p in range(lower_bound + 2, len(self.tags), 1):
                    if self.persist[self.tags[p]] == YES:
                        upper_bound_persist = str(p)
                        break
                right = float(rtag)
                upper_bound_persist = float(self.tags[upper_bound_persist])
                left = float(ltag) + index * (upper_bound_persist - float(ltag)) / no_of_users
            print left, right, ' = here insert'
            if found is True:
                self.add(left, right, ch)
        print self.piece(0, 1)

    def delete(self, pos):
        count = 0
        found = False
        for tag in self.tags:
            if self.pps[tag] != PHI:
                count += 1
            if count == pos:
                found = True
                break
        if found is True:
            self.hide(float(self.tags[count]))

        print self.piece(0, 1)

    def piece(self, pos_stamp_left, pos_stamp_right):
        if str(pos_stamp_left) not in self.tags or str(pos_stamp_right) not in self.tags:
            return ""
        left = self.tags.index(str(pos_stamp_left))
        right = self.tags.index(str(pos_stamp_right))
        cur_doc = ""
        count = 0
        for tag in self.tags:
            if (left <= count < right) and self.pps[tag] != '0':
                cur_doc += self.pps[tag]
            count += 1
        return cur_doc
