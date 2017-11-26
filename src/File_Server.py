from flask import Flask, make_response, request
from flask_restful import inputs, reqparse, Api, fields, marshal, Resource, abort
import requests
from utils import get_file_read, get_file_write
import sys
from format import format_node_req
import json


"""Server deployed by 'python File_Server.py [Server port] [Path where server files are stored (relative to src)]' """

app = Flask(__name__)
api = Api(app)
FILE_SERVER_PATH = ""

class File_API(Resource):

    def get(self, file_name):
        file = get_file_read(file_name, FILE_SERVER_PATH)
        print("Received request for " + file_name)
        if(file == None):
            abort(404)
        else:
            print("Sending back the following content: ", file)
            response = {
                "file_name": file_name,
                "file_content": file
                }
            return response
    
    def post(self, file_name):
        file = get_file_write(file_name, FILE_SERVER_PATH)
        print("Received request for " + file_name)
        if(file == None):
            abort(404)
        else:
            #TODO: this is a temporary precaution
            content = request.json
            print("Content received: ", content)
            if(content != None and request.is_json):
                print("Performing write")
                file.write(content["file_content"])
                response = {
                    "status": "Success"
                }
                return response
            else:
                print("Request data is none")
            
        

api.add_resource(File_API, '/api/files/<string:file_name>', endpoint = 'file')

if __name__ == '__main__':
    
    server_port = int(sys.argv[1])
    dir_server_port = sys.argv[2]

    url = format_node_req(server_port, dir_server_port)
    print("Sending the following request: ", url)
    files = requests.get(url).content.decode()
    json_data = json.loads(files)

    if(files != None):
        print("Setting file server path")
        FILE_SERVER_PATH = json_data["file_dir"]

    app.run(host= '0.0.0.0', port = server_port, debug = False)
    print("File server node running on port: ", server_port)

