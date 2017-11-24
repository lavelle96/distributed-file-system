from flask import Flask
from flask_restful import Api, Resource
import requests
from format import format_file_req
import sys
import json

app = Flask(__name__)
api = Api(app)

#Map of directories to whether they have a file server managing them

DIR_MAP = {
    'D1':False,
    'D2':False
}
FILE_MAP = {
    '1.1':'D1',
    '1.2':'D1',
    '2.1':'D2',
    '2.2':'D2'
}
#Map of Directory to Node
ACTIVE_NODES = {}

class Directory_API(Resource):
    def get(self, file_name):
        if file_name in FILE_MAP.keys() and DIR_MAP[FILE_MAP[file_name]] == True:
            url = format_file_req(file_name, ACTIVE_NODES[FILE_MAP[file_name]])
            print(url)
            response1 = json.loads(requests.get(url).content.decode())
            return response1
            


class Node_Init_API(Resource):
    def get(self, port_number):
        
        for key in ACTIVE_NODES:
            if ACTIVE_NODES[key] == port_number:
                response = {"file_dir": key}
                return response
        
        for dir in DIR_MAP:
            if DIR_MAP[dir] == False:
                DIR_MAP[dir] = True
                ACTIVE_NODES[dir] = port_number
                print('directory: ' + dir + ' given to port: ' + port_number)
                response = {"file_dir": dir}
                return response
        return None


api.add_resource(Directory_API, '/api/files/<string:file_name>', endpoint = 'file')
api.add_resource(Node_Init_API, '/api/node/<string:port_number>', endpoint = 'node')

if __name__ == '__main__':
     server_port = int(sys.argv[1])
     app.run(host= '0.0.0.0', port = server_port, debug = True)
