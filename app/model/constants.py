import json
from apiclient.discovery import build

APPLICATION_NAME = 'ZooDel'
SERVICE = build('plus', 'v1')
CLIENT_ID = json.loads(open("app/static/data/client_secrets.json", 'r').read())['web']['client_id']

PPS_STRUCT = 'pps'
POS_TAGS = 'pps_pos_tags'
USERS = 'users'
KEYS = 'user_doc_key'
PERSIST = 'persistent'
YES = 'YES'
NO = 'NO'
PHI = '0'
CURSOR_POS = 'cursor_pos'
CURSOR_COLOR = 'cursor_color'
