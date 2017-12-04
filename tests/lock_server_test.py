import requests
import sys
sys.path.insert(0, '/home/lavelld/Documents/SS/Internet_Apps/DFS/src')
from format import format_lock_req
import config as cf
import json

#client 1 gets lock
url = format_lock_req('1.1', '0', cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
id1 = response['client_id']
print('id1: ', id1)
print(response)

#client 1 accidently send request again but still gets lock
url = format_lock_req('1.1', id1, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

#client 2 gets rejected for lock
url = format_lock_req('1.1', 0, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
id2 = response['client_id']
print('id2: ', id2)
print(response)

#client 3 gets rejected for lock
url = format_lock_req('1.1', 0, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
id3 = response['client_id']
print('id3: ', id3)
print(response)

#client 1 releases lock
url = format_lock_req('1.1', id1, cf.LOCK_SERVER_PORT)
response = json.loads(requests.post(url).content.decode())
print(response)

#client 3 gets rejected for lock
url = format_lock_req('1.1', id3, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

#client 2 gets lock
url = format_lock_req('1.1', id2, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

#client 1 gets rejected for lock
url = format_lock_req('1.1', id1, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

#client 2 releases lock
url = format_lock_req('1.1', id2, cf.LOCK_SERVER_PORT)
response = json.loads(requests.post(url).content.decode())
print(response)

#client 3 gets lock
url = format_lock_req('1.1', id3, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

#client 3 releases lock
url = format_lock_req('1.1', id3, cf.LOCK_SERVER_PORT)
response = json.loads(requests.post(url).content.decode())
print(response)

#client 1 gets lock
url = format_lock_req('1.1', id1, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

#client 1 releases lock
url = format_lock_req('1.1', id1, cf.LOCK_SERVER_PORT)
response = json.loads(requests.post(url).content.decode())
print(response)

#Check if still successful after emptied
#client 3 gets lock
url = format_lock_req('1.1', id3, cf.LOCK_SERVER_PORT)
response = json.loads(requests.get(url).content.decode())
print(response)

#client 3 releases lock
url = format_lock_req('1.1', id3, cf.LOCK_SERVER_PORT)
response = json.loads(requests.post(url).content.decode())
print(response)