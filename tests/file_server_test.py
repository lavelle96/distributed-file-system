import requests
import sys
sys.path.insert(0, '/home/lavelld/Documents/SS/Internet_Apps/DFS/src')
from format import format_file_req, format_registry_req
import config as cf
import json

file_name = '1.1'
file_content = 'Test generated content for file ' + file_name
dir_port_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
response = json.loads(requests.get(dir_port_url).content.decode())
dir_server_port = response['dir_port']

url = format_file_req(file_name, dir_server_port)
response =  json.loads(requests.get(url).content.decode())
file_server_port = response['file_server_port']

req = format_file_req(file_name, file_server_port)
data = {
            'file_name': file_name,
            'file_content': file_content,
            'replicate': True
        }
response = requests.post(req, data=json.dumps(data), headers = cf.JSON_HEADER)
print(response)