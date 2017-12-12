from flask import Flask, request, abort
from flask_restful import Api, Resource
from pymongo import MongoClient
from format import format_ports_req, format_registry_req, format_file_req
import requests
import json
import config as cf
import sys

app = Flask(__name__)
api = Api(app)

class replication_API(Resource):
    def post(self):
        '''
        data={
            file_name:
            file_content:
            dir_name:
            fs_port:
        }
        '''
        
        if(not request.is_json):
            abort(400)
        data = request.json
       
        dir_name = data['dir_name']
        fs_port = data['fs_port']
        file_name = data['file_name']
        file_content = data['file_content']

        #Get directory server port number
        dir_port_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
        response = json.loads(requests.get(dir_port_url).content.decode())
        dir_server_port = response['dir_port']

        #Get ports of fs's handling the same directory
        req = format_ports_req(dir_name, dir_server_port)
        response = json.loads(requests.get(req).content.decode())
        ports = response['ports']
        
        data = {
            'file_name': file_name,
            'file_content': file_content,
            'replicate': False
        }
        print('request to replicate received from ', fs_port)
        for port in ports:
            if str(port) != str(fs_port):
                print('sending request to ', port)
                req = format_file_req(file_name, port)
                requests.post(req, data=json.dumps(data), headers = cf.JSON_HEADER)
                print('request sent to, ', port)
        print('finished replication')
        return 

class state_API(Resource):
    '''Api that allows calls to check the state and shutdown the server'''
    def get(self):
        response = {
            'state': 'running'
        }
        return response

    def delete(self):
        request.environ.get('werkzeug.server.shutdown')()
        response = {
            'state': 'shutting down'
        }
        return response



api.add_resource(state_API, '/api/state')
api.add_resource(replication_API, '/api/replicate')

if __name__ == '__main__':
    server_port = sys.argv[1]

    server_init_url = format_registry_req('rep_server', cf.REGISTRY_SERVER_PORT)
    data = {
        'dir_port': server_port
    }
    requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)

    app.run('0.0.0.0', server_port)