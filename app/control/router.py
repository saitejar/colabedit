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
    print 'hearbeat -', cur_text
    response = make_response(json.dumps(cur_text), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    # response.headers['DOC'] = doc
    return response


@router.route('/login', methods=['POST'])
def initialize():
    response = make_response(json.dumps('initialized successfully'), 200)
    username = request.json['userName']
    UserOrder(doc='').add(username)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response


@router.route('/deinitializeCall', methods=['POST'])
def deinitialize():
    response = make_response(json.dumps('deinitialized successfully'), 200)
    username = request.json['userName']
    UserOrder(doc='').add(username)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response


@router.route('/dummy', methods=['POST'])
def login():
    username = request.json['userName']
    response = make_response(json.dumps(username), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response
