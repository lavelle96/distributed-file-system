from flask import Flask, request
from flask_restful import Api, Resource, abort
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
            #Reformat so that its passed in python map object form and not twice changed into string form
            
            response = json.loads(requests.get(url).content.decode())
            print("Sending this response on: ", response)
            return response
        else:
            abort(404)

    def post(self, file_name):
        """If file exists, route it on to the correct server"""
        print('post request received')
        if file_name in FILE_MAP.keys() and DIR_MAP[FILE_MAP[file_name]] == True:
            url = format_file_req(file_name, ACTIVE_NODES[FILE_MAP[file_name]])
            
            print ("Is it json: ", request.is_json)
            content = request.get_json()
            print ("Content: ", content)
            headers =  {'content-type': 'application/json'}
            response = json.loads(requests.post(url, data = request.data, headers = headers).content.decode())
            return response
        else:
            print("File doesnt exist or is not on one of our servers")
            abort(404)


class Node_Init_API(Resource):
    def get(self, port_number):
        print("Request received from port: ", port_number)
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
