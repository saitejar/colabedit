import json
from apiclient.discovery import build

APPLICATION_NAME = 'ZooDel'
SERVICE = build('plus', 'v1')

PPS_STRUCT = 'pps'
POS_TAGS = 'pps_pos_tags'
USERS = 'users'
MAIN_PPS = 'main_pps'
KEYS = 'user_doc_key'
PERSIST = 'persistent'
YES = 'YES'
NO = 'NO'
PHI = '0'
CURSOR_POS = 'cursor_pos'
CURSOR_COLOR = 'cursor_color'