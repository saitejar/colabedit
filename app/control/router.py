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
    reply = {}
    users = UserOrder(doc='')
    reply['userCount'] = users.count()
    reply['userPosition'] = users.index(username.lower())
    print 'seq number ' + str(request.json['lastGreatestSequenceNumber'])
    last_received_change = int(request.json['lastGreatestSequenceNumber'])
    users = UserOrder(doc='')
    reply['transactions'] = {}
    ids = sorted([int(key) for key in users.changes.keys() if int(key) > last_received_change])
    print 'acaaakaa ' + str(users.user_changes[username.lower()]) + " and " + str(users.user_changes)
    cur_user_ids = []
    for id in users.user_changes[username.lower()].split(','):
        if id != '':
            cur_user_ids.append(int(id))
    ids = set(ids).difference(set(cur_user_ids))
    for change_id in ids:
        reply['transactions'][id] = json.loads(users.changes[change_id])
    response = make_response(json.dumps(reply), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response

@router.route('/sendUserNames', methods=['POST'])
def sendUserNames():
    users = UserOrder(doc='')
    response = make_response(json.dumps(users.users.keys()), 200)
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
    try:
        response = make_response(json.dumps('deinitialized successfully'), 200)
        username = request.json['userName']
        if username != "":
            UserOrder(doc='').remove(username)
        response.headers['Content-Type'] = 'application/json;charset=UTF-8'
        return response
    except:
        response = make_response(json.dumps('deinitialized successfully'), 200)
        response.headers['Content-Type'] = 'application/json;charset=UTF-8'
        return response


@router.route('/sendChanges', methods=['POST'])
def insertText():
    response = make_response(json.dumps('success'), 200)
    pendingChanges = request.json['changesToBePushed']
    username = request.json['userName']
    users = UserOrder(doc='')

    pps = PPS()
    for key in pendingChanges.keys():
        if key == 'insert':
            pps.attach(pendingChanges[key][0], pendingChanges[key][1])
        elif key == 'delete':
            pps.hide(pendingChanges[key])

    id = users.get_change_id()
    users.changes[id] = json.dumps(pendingChanges)
    reply = {'id': id}
    if users.user_changes[username.lower()]=='':
        users.user_changes[username.lower()] += str(id)
    else:
        users.user_changes[username.lower()] += ',' + str(id)
    response = make_response(json.dumps(reply), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response
