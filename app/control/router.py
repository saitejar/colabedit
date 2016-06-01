import logging
import json
from google.appengine.ext import vendor
from flask.ext.socketio import SocketIO, emit
from flask import request, send_file, session, make_response, render_template, Blueprint, jsonify, request, Flask
from ..model.redis_db import redis_manager
from ..model.user_order import UserOrder
from ..model.pps import PPS

vendor.add("lib")
router = Blueprint('router', __name__)


@router.route('/', methods=['GET'])
def index():
    response = make_response(render_template('index.html'))
    response.headers['Content-Type'] = 'text/html;charset=UTF-8'
    return response


@router.route('/heartbeat', methods=['POST'])
def heartbeat():
    cursor_position = request.json['cursorPosition']
    username = request.json['userName']
    timestamp = request.json['timeStamp']
    print request.json
    last_received_change = int(request.json['lastGreatestSequenceNumber'])
    cur_text = PPS().piece(0, 1)
    reply = {}
    users = UserOrder(doc='')
    reply['userCount'] = users.count()
    reply['userPosition'] = users.index(username.lower())
    reply['transactions'] = {}
    ids = [int(key) for key in users.changes.keys() if int(key) > last_received_change]
    for id in ids:
        reply['transactions'][id] = json.loads(users.changes[id])

    response = make_response(json.dumps(reply), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response


@router.route('/login', methods=['POST'])
def initialize():
    username = request.json['userName']
    if(UserOrder(doc='').index(username.lower()) == -1):
        UserOrder(doc='').add(username)
        response = make_response("{\"userCount\" : \"" + str(UserOrder(doc='').count()) + "\", \"userPosition\" : \"" + str(UserOrder(doc='').index(username.lower())) + "\"}", 200)
        response.headers['Content-Type'] = 'application/json;charset=UTF-8'
        return response
    else:
        response = make_response(json.dumps('invalid'), 200)
        response.headers['Content-Type'] = 'application/json;charset=UTF-8'
        return response


@router.route('/deinitializeCall', methods=['POST'])
def deinitialize():
    response = make_response(json.dumps('deinitialized successfully'), 200)
    username = request.json['userName']
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response


@router.route('/sendChanges', methods=['POST'])
def insertText():
    response = make_response(json.dumps('success'), 200)
    print request.json['changesToBePushed']
    pendingChanges = request.json['changesToBePushed']
    pps = PPS()
    for key in pendingChanges.keys():
        if key == 'insert':
            pps.attach( pendingChanges[key][0], pendingChanges[key][1])
        elif key == 'delete':
            pps.hide(pendingChanges[key])
    users = UserOrder()
    id = users.get_change_id()
    users.changes[id] = json.dumps(pendingChanges)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response
