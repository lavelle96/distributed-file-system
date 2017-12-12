from flask import Flask, make_response, request
from flask_restful import inputs, reqparse, Api, fields, marshal, Resource, abort
import requests
from utils import get_file_read, get_file_write, get_files_in_dir, split_path
import sys
from format import format_node_req, format_registry_req, format_replication_req
import json
import config as cf


"""Server deployed by 'python File_Server.py [Server port] [Path where server files are stored (relative to src)]' """

app = Flask(__name__)
api = Api(app)
FILE_SERVER_PATH = ""
SERVER_PORT = 0
ROOT_DIR = ""


class File_API(Resource):

    def get(self, file_name):
        '''Read file'''
        print( 'looking for file: ', file_name, ' in ', FILE_SERVER_PATH)
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
        '''write to file
        request format:
        {
            file_name:
            file_content:
            replicate: (if replicate = true send request onto the replication server)
        }'''
        file = get_file_write(file_name, FILE_SERVER_PATH)
        print("Received request for " + file_name)
        if(file == None):
            abort(404)
        else:
            content = request.json
            print("Content received: ", content)
            if(content != None and request.is_json):
                print("Performing write")
                try:
                    file.write(content["file_content"])
                except:
                    print('write failed')
                    return
                response = {
                    "status": "Success"
                }
                
                if content['replicate'] == True:
                    print('replicating write')
                    #Find replication port
                    rep_port_url = format_registry_req('rep_server', cf.REGISTRY_SERVER_PORT)
                    response = json.loads(requests.get(rep_port_url).content.decode())
                    rep_server_port = response['dir_port']
                    #Send post onto replication server
                    req = format_replication_req(rep_server_port)
                    data = {
                        'file_name': file_name,
                        'file_content': content['file_content'],
                        'dir_name': ROOT_DIR,
                        'fs_port': SERVER_PORT
                    }
                    requests.post(req, data=json.dumps(data), headers=cf.JSON_HEADER)

                return response
            else:
                print("Request data is none")
            
        

api.add_resource(File_API, '/api/files/<string:file_name>', endpoint = 'file')

if __name__ == '__main__':
    
    #FIle server post given as argument
    SERVER_PORT = int(sys.argv[1])
    #File path given as second argument e.g. FS_1
    file_path = sys.argv[2]
    FILE_SERVER_PATH = file_path

    #Register with registry server
    server_init_url = format_registry_req('file_server', cf.REGISTRY_SERVER_PORT)
    data = {
        'dir_port': SERVER_PORT
    }
    requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)

    #Get dir server port
    dir_port_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
    response = json.loads(requests.get(dir_port_url).content.decode())
    dir_server_port = response['dir_port']

    file_paths = get_files_in_dir(FILE_SERVER_PATH)
    dir_name = split_path(file_paths[0])[0]
    ROOT_DIR = dir_name
    FILE_SERVER_PATH  = FILE_SERVER_PATH + '/' + dir_name
    file_names = []
    for f in file_paths:
        file_name = split_path(f)[1]
        file_names.append(file_name)
    data = {
        'dir_name': dir_name,
        'file_names': file_names
    }
    #Send batch of files
    url = format_node_req(SERVER_PORT, dir_server_port)
    requests.post(url, data=json.dumps(data), headers= cf.JSON_HEADER).content.decode()
    

    

    app.run(host= '0.0.0.0', port = SERVER_PORT, debug = False)
    print("File server node running on port: ", SERVER_PORT)

