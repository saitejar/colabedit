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
from model.redis_db import redis_manager
from model.pps import PPS

app = flask.Flask(__name__)
app.debug = True

app.register_blueprint(router, url_prefix='')
sio = SocketIO(app)
redis_manager.flushall()


@sio.on('insert', namespace='/insert')
def insert(message):
    print 'hello inset'
    ch = int(message['char'])
    pos = int(message['pos'])
    user = message['userName']
    pps = PPS(user=user)
    if int(message['char']) == 8:
        pps.delete(pos)
    elif int(message['char']) != 8:
        print 'insertinggggg'
        pps.insert(ch, pos)
    else:
        pass

    emit('keyPressEventSocket',
         {'data': message['char'], 'position': message['pos'], 'sid': request.sid, 'user': message['userName']})

if __name__ == '__main__':
    app.run()
