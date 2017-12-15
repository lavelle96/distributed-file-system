import requests
import sys
sys.path.insert(0, '/home/lavelld/Documents/SS/Internet_Apps/DFS/src')
from format import format_login_req, format_admin_req, format_users_req
import config as cf
import json

#Valid admin request
req = format_admin_req(cf.AUTH_SERVER_PORT)
data = {
    'admin_username': 'lavelld',
    'admin_password': 'plavelld'
}
response = json.loads(requests.get(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
print(response)

#Invalid admin request
req = format_admin_req(cf.AUTH_SERVER_PORT)
data = {
    'admin_username': 'lavell',
    'admin_password': 'plavell'
}
response = json.loads(requests.get(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
print(response)

#Admin_add
req = format_admin_req(cf.AUTH_SERVER_PORT)
data= {
    'admin_username': 'lavelld',
    'admin_password': 'plavelld',
    'new_username': 'new_user',
    'new_password': 'pnew_user',
    'new_privilege': 'user'
}
response = json.loads(requests.post(req, data= json.dumps(data), headers=cf.JSON_HEADER).content.decode())
print(response)

#New user login
req = format_login_req(cf.AUTH_SERVER_PORT)
data = {
    'username': 'new_user',
    'password': 'pnew_user'
}
response = json.loads(requests.get(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
print(response)

#list users
req = format_users_req(cf.AUTH_SERVER_PORT)
data = {
    'admin_username': 'lavelld',
    'admin_password': 'plavelld'
}
response = json.loads(requests.get(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
print(response)
