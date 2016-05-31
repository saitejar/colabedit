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
    cur_text = PPS().piece(0, 1)
    response = make_response("{\"userCount\" : \"" + str(UserOrder(doc='').count()) + "\", \"userPosition\" : \"" + str(UserOrder(doc='').index(username.lower())) + "\"}", 200)
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
    pendingChanges = request.json['changesToBePushed']
    print "PENDING TO INSERT : " + str(pendingChanges)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response
