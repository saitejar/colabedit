import logging
import json
from google.appengine.ext import vendor
from flask.ext.socketio import SocketIO, emit
from flask import request, send_file, session, make_response, render_template, Blueprint, jsonify, request, Flask
from ..model.redis_db import redis_manager

vendor.add("lib")
signin_api_blueprint = Blueprint('signin', __name__)

@signin_api_blueprint.route('/', methods=['GET'])
def index():
    response = make_response(render_template('index.html'))
    response.headers['Content-Type'] = 'text/html;charset=UTF-8'
    return response

@signin_api_blueprint.route('/heartbeat', methods=['POST'])
def heartbeat():
    pps_pos = redis_manager.zrange('PPS_POS', 0, -1)
    doc = ''
    for pos in pps_pos:
        doc += str(redis_manager.hget('PPS_MAP', str(pos)))

    response = make_response(json.dumps(doc), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    # response.headers['DOC'] = doc
    return response


@signin_api_blueprint.route('/initializeCall', methods=['POST'])
def initializeCall():
    response = make_response(json.dumps('initialized successfully'), 200)

    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response


@signin_api_blueprint.route('/deinitializeCall', methods=['POST'])
def deinitializeCall():
    response = make_response(json.dumps('deinitialized successfully'), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response


@signin_api_blueprint.route('/clearTextArea', methods=['POST'])
def clearTextArea():
    logging.info("IN THE CLEARING")
    redis_manager.flushall();
    response = make_response(json.dumps('cleared'), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response

@signin_api_blueprint.route('/login', methods=['POST'])
def login():
    userName = request.json['username']
    response = make_response(json.dumps(userName), 200)
    response.headers['Content-Type'] = 'application/json;charset=UTF-8'
    return response
