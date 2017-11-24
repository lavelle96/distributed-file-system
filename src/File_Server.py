from flask import Flask, make_response
from flask_restful import inputs, reqparse, Api, fields, marshal, Resource, abort
import requests
from utils import get_file
import config
import sys
from format import format_node_req
import json


"""Server deployed by File_Server.py [Server port] [Path where server files are stored (relative to src)]"""

app = Flask(__name__)
api = Api(app)
FILE_SERVER_PATH = ""

class File_API(Resource):

    def get(self, file_name):
        file = get_file(file_name, FILE_SERVER_PATH)
        print("Received request for " + file_name)
        if(file == None):
            abort(404)
        else:
            print("Sending " + file_name + " back: " + file)
            return file
        

api.add_resource(File_API, '/api/files/<string:file_name>', endpoint = 'file')

if __name__ == '__main__':
    server_port = int(sys.argv[1])
    dir_server_port = sys.argv[2]
    request_made = False
    url = format_node_req(server_port, dir_server_port)
    
    
    files = requests.get(url).content.decode()
    json_data = json.loads(files)
    print(json_data["file_dir"])
   
    
    if(files != None):
        FILE_SERVER_PATH = json_data["file_dir"]
    
    
    app.run(host= '0.0.0.0', port = server_port, debug = True)