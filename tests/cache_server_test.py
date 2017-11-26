import requests
import sys
sys.path.insert(0, '/home/lavelld/Documents/SS/Internet_Apps/DFS/src')
from format import format_file_req
import json



if __name__ == '__main__':
    cache_server_port = sys.argv[1]
    file_name = '1.4'
    data = {
        'file_name': file_name,
        'file_content': 'hello there sir'
    }
    JSON_HEADER = {'content-type': 'application/json'}

    url = format_file_req(file_name, cache_server_port)
    response = requests.post(url, data=json.dumps(data), headers = JSON_HEADER)
    #response = requests.get(url)
    response = response.content
    print(response)