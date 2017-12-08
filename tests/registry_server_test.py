import sys
sys.path.insert(0, '/home/lavelld/Documents/SS/Internet_Apps/DFS/src')
from format import format_registry_req
import requests
import config as cf
import json

url = format_registry_req('file_server', cf.REGISTRY_SERVER_PORT)
data = {'dir_port': 5001}
requests.post(url, data=json.dumps(data), headers=cf.JSON_HEADER)

url = format_registry_req('file_server', cf.REGISTRY_SERVER_PORT)
data = {'dir_port': 5002}
requests.post(url, data=json.dumps(data), headers=cf.JSON_HEADER)

url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
data = {'dir_port': 5003}
requests.post(url, data=json.dumps(data), headers=cf.JSON_HEADER)

url = format_registry_req('lock_server', cf.REGISTRY_SERVER_PORT)
data = {'dir_port': 5004}
requests.post(url, data=json.dumps(data), headers=cf.JSON_HEADER)

url = format_registry_req('file_server', cf.REGISTRY_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print('file server 1 response: ', response)

url = format_registry_req('file_server', cf.REGISTRY_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print('file server 2 response: ', response)

url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print('dir server response: ', response)

url = format_registry_req('lock_server', cf.REGISTRY_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print('lock server response: ', response)
