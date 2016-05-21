# coding: utf-8

import control
import flask
import model
import random
import string
import logging
from flask.ext.socketio import SocketIO, emit
from flask import request
from control.signin import signin_api_blueprint
from simplekv.memory import DictStore
from flask_kvsession import KVSessionExtension
from model.redis_db import redis_manager

app = flask.Flask(__name__)
app.debug = True
store = DictStore()
KVSessionExtension(store, app)
app.register_blueprint(signin_api_blueprint, url_prefix='')
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for x in xrange(32))
sio = SocketIO(app)


@sio.on('insert', namespace='/insert')
def insert(message):
    logging.info("Request from SID : " + request.sid)  # Unique session Identifier for client
    ch = chr(int(message['char']))
    pos = int(message['pos'])
    pps_pos = 0.01 * pos
    redis_manager.zadd('PPS_POS', str(pps_pos), pps_pos)
    dump = ' '.join(redis_manager.zrange('PPS_POS', 0, -1))
    logging.info('DUMP : ' + dump)
    redis_manager.hset('PPS_MAP', pps_pos, ch)
    emit('insert', {'data': message['char'], 'position': message['pos'], 'sid': request.sid})


if __name__ == '__main__':
    app.run()
