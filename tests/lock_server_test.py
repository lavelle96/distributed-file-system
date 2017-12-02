import requests
import sys
sys.path.insert(0, '/home/lavelld/Documents/SS/Internet_Apps/DFS/src')
from format import format_lock_req
import config as cf
import json

url = format_lock_req('1.1', '0', cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

url = format_lock_req('1.1', response['client_id'], cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

url = format_lock_req('1.1', 0, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)