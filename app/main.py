# coding: utf-8

import control
import flask
import model
import random
import string
import logging
from flask.ext.socketio import SocketIO, emit
from flask import request
from control.router import router
from simplekv.memory import DictStore
from flask_kvsession import KVSessionExtension
from model.redis_db import redis_manager
from model.pps import PPS

app = flask.Flask(__name__)
app.debug = True
store = DictStore()
KVSessionExtension(store, app)
app.register_blueprint(router, url_prefix='')
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for x in xrange(32))
sio = SocketIO(app)


@sio.on('insert', namespace='/insert')
def insert(message):
    ch = int(message['char'])
    pos = int(message['pos'])
    pps = PPS(message['userName'])
    if int(message['char']) == 8:
        pps.delete(pos)
    elif int(message['char']) != 8:
        pps.insert(ch, pos)
    else:
        pass

    emit('keyPressEventSocket',
         {'data': message['char'], 'position': message['pos'], 'sid': request.sid, 'user': message['userName']})


if __name__ == '__main__':
    redis_manager.flushall()
    app.run()
