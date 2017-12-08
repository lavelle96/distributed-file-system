from flask import Flask, request, jsonify
from flask_restful import Api, Resource, abort
import requests
from format import format_file_req, format_registry_req
import sys
import json
from pymongo import MongoClient
import config as cf


client = MongoClient()
db = client.dir_db
file_map = db.file_map
dir_map = db.dir_map
active_nodes = db.active_nodes
'''
{
    'port':
    'dir':
    'load':
    
}
'''
app = Flask(__name__)
api = Api(app)

#Map of directories to whether they have a file server managing them


FILE_11 = {
    'name': '1.1',
    'dir': 'D1'
}
FILE_12 = {
    'name': '1.2',
    'dir': 'D1'
}
FILE_21 = {
    'name': '2.1',
    'dir': 'D2'
}
FILE_22 = {
    'name': '2.2',
    'dir': 'D2'
}
DIR_1 = {
    'name': 'D1',
    'num_nodes': 0,
    'ports': []
}
DIR_2 = {
    'name': 'D2',
    'num_nodes': 0,
    'ports': []
    }
#Map of Directory to Node

class Directory_API(Resource):
    def get(self, file_name):
        
        f = file_map.find_one({'name': file_name})
        if f == None:
            abort(404)
        file_dir = f['dir']
        d = dir_map.find_one({'name': file_dir})
        if d['num_nodes'] == 0:
            abort(404)

        nodes = active_nodes.find({'dir': file_dir})
        min_load = None
        port = 0
        for node in nodes:
            if min_load == None or node['load'] < min_load:
                min_load = node['load']
                port = node['port']

        active_nodes.update_one(
            {'port': port},
            {
                '$inc': {
                    'load': 1
                }
            }
        )

        response = {
            'file_server_port': port
        }
        return jsonify(response)

class Node_Init_API(Resource):
    def get(self, port_number):
        dirs = dir_map.find()

        directory_to_return = None
        min_nodes = None
        for d in dirs:
            ports = d['ports']
            #If port is already registered
            if port_number in ports:
                response = {"file_dir": d['name']}
                return response
            #otherwise return port with least amount of nodes
            print('nodes on dir: ', d['name'], ' ', d['num_nodes'])
            if min_nodes == None:
                print('new min: ', d['num_nodes'])
                min_nodes = d['num_nodes'] 
                directory_to_return = d
            elif d['num_nodes'] < min_nodes:
                print('new min: ', d['num_nodes'])
                min_nodes = d['num_nodes'] 
                directory_to_return = d
        
        print('directory chosen to return: ', d)
        #append port number to list
        p_list = directory_to_return['ports']
        p_list.append(port_number)
        
        #Increase number of nodes
        num_nodes = directory_to_return['num_nodes']
        num_nodes += 1

        name = directory_to_return['name']

        dir_map.update_one(
            {'name': name},
            {
                '$set':{
                    'ports': p_list,
                    'num_nodes': num_nodes
                }
            }
        )

        new_node = {
            'port': port_number,
            'dir': name,
            'load': 0
        }
        active_nodes.insert_one(new_node)

        response = {
            "file_dir": name
        }
        print('response to port ', str(port_number), ' ', response)
        return jsonify(response)



api.add_resource(Directory_API, '/api/files/<string:file_name>', endpoint = 'file')
api.add_resource(Node_Init_API, '/api/node/<string:port_number>', endpoint = 'node')

if __name__ == '__main__':
    db.drop_collection('file_map')
    db.drop_collection('dir_map')
    db.drop_collection('active_nodes')
    file_map.insert_many([FILE_11, FILE_12, FILE_21, FILE_22])
    dir_map.insert_many([DIR_1, DIR_2])
    server_port = int(sys.argv[1])

    server_init_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
    data = {
        'dir_port': server_port
    }
    requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)
    app.run(host= '0.0.0.0', port = server_port, debug = True)
