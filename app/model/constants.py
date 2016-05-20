import json
from apiclient.discovery import build

APPLICATION_NAME = 'ZooDel'
SERVICE = build('plus', 'v1')
CLIENT_ID = json.loads(
    open("app/static/data/client_secrets.json", 'r').read())['web']['client_id']


PPS = 'pps'
USER_ORDER = 'user_order'