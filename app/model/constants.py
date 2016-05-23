import json
from apiclient.discovery import build

APPLICATION_NAME = 'ZooDel'
SERVICE = build('plus', 'v1')
CLIENT_ID = json.loads(open("app/static/data/client_secrets.json", 'r').read())['web']['client_id']


PPS_STRUCT = 'pps'
POS_TAGS = 'pps_pos_tags'
USER_ORDER = 'user_order'
KEYS = 'user_doc_key'
PERSIST = 'persistent'
YES = 'YES'
NO = 'NO'
