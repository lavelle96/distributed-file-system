import requests
import sys
sys.path.insert(0, '/home/lavelld/Documents/SS/Internet_Apps/DFS/src')
from format import format_node_req, format_file_req


dir_port = 5002
#Set up 4 file servers
req_1 = format_node_req(6001, dir_port)
req_2 = format_node_req(6002, dir_port)
req_3 = format_node_req(6003, dir_port)
req_4 = format_node_req(6004, dir_port)

print(requests.get(req_1).content.decode())
print(requests.get(req_2).content.decode())
print(requests.get(req_3).content.decode())
print(requests.get(req_4).content.decode())

#Request 2 files from two different directories
req_5 = format_file_req('1.1', dir_port)
req_6 = format_file_req('1.2', dir_port)
req_7 = format_file_req('2.1', dir_port)
req_8 = format_file_req('2.2', dir_port)

print(requests.get(req_5).content.decode())
print(requests.get(req_6).content.decode())
print(requests.get(req_7).content.decode())
print(requests.get(req_8).content.decode())

