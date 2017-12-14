from flask import Flask, make_response, request
from flask_restful import inputs, reqparse, Api, fields, marshal, Resource, abort
import requests
from utils import get_file_read, get_file_write, get_files_in_dir, split_path, get_port
import sys
from format import format_node_req, format_registry_req, format_replication_req, format_node_req
import json
import config as cf


"""Server deployed by 'python File_Server.py [Server port] [Path where server files are stored (relative to src)]' """

app = Flask(__name__)
api = Api(app)
FILE_SERVER_PATH = ""
SERVER_PORT = 0
ROOT_DIR = ""


class File_API(Resource):

    def get(self):
        '''Read file'''
        data = request.json
        file_name = data['file_name']
        print( 'looking for file: ', file_name, ' in ', FILE_SERVER_PATH)
        
        file_content = get_file_read(file_name, FILE_SERVER_PATH)
        if(file_content == None):
            abort(404)
        else:
            print("Sending back the following content: ", file_content)
            response = {
                "file_name": file_name,
                "file_content": file_content
                }
            return response
    
    def post(self):
        '''write to file
        request format:
        {
            file_name:
            file_content:
            replicate: (if replicate = true send request onto the replication server)
        }'''
        content = request.json
        file_name = content['file_name']
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
            
        
class state_API(Resource):
    '''Api that allows calls to check the state and shutdown the server'''
    def get(self):
        response = {
            'state': 'running'
        }
        return response

    def delete(self):
        #Alert directory server first
        dir_port = get_port('dir_server')
        if dir_port:
            req = format_node_req(SERVER_PORT, dir_port)
            requests.delete(req)
        request.environ.get('werkzeug.server.shutdown')()
        response = {
            'state': 'shutting down'
        }
        return response



api.add_resource(state_API, '/api/state')
api.add_resource(File_API, '/api/file', endpoint = 'file')

if __name__ == '__main__':
    
    #FIle server post given as argument
    SERVER_PORT = int(sys.argv[1])
    #File path given as second argument e.g. FS_1
    file_path = sys.argv[2]
    FILE_SERVER_PATH = file_path

    #Register with registry server
    try:
        server_init_url = format_registry_req('file_server', cf.REGISTRY_SERVER_PORT)
        data = {
            'dir_port': SERVER_PORT
        }
        requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)
    except:
        print('Registry server not ready')
        sys.exit(1)

    #Get dir server port
    try:
        dir_port_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
        response = json.loads(requests.get(dir_port_url).content.decode())
        dir_server_port = response['dir_port']
        if str(dir_server_port) == str(-1):
            sys.exit()
    except:
        print('No directory port up yet')
        sys.exit()
    file_names = get_files_in_dir(FILE_SERVER_PATH)
    
    data = {
        'file_names': file_names
    }
    #Send batch of files
  
    url = format_node_req(SERVER_PORT, dir_server_port)
    requests.post(url, data=json.dumps(data), headers= cf.JSON_HEADER).content.decode()
    
    app.run(host= '0.0.0.0', port = SERVER_PORT, debug = False)
    print("File server node running on port: ", SERVER_PORT)

