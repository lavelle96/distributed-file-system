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
'''
{
    'name':
    'dir':
}   
'''
dir_map = db.dir_map
'''{
    'name':
    'num_nodes':
    'ports':
}'''
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

    def post(self, port_number):
        '''
        Allows file servers to post the name of their directory and all the files contained in it
        request data:
        data={
            dir_name:
            file_names:[]
        }
        '''
        if(not request.is_json):
            abort(400)
        data = request.json
        print('new node up and running, data: ', data)
        dir_name = data['dir_name']
        new_node = {
            'port': port_number,
            'dir': dir_name,
            'load': 0
        }
        active_nodes.insert_one(new_node)
        file_names = data['file_names']
        dir_info = dir_map.find_one({'name': dir_name})
        if dir_info == None:
            #Create directory
            new_dir = {
                'name': dir_name,
                'num_nodes': 1,
                'ports': [port_number]
            }
            dir_map.insert_one(new_dir)
            for f in file_names:
                new_file = {
                    'name': f,
                    'dir': dir_name
                }
                file_map.insert_one(new_file)
        else:
            #Add port as a node on that directory
            port_list = dir_info['ports']
            port_list.append(port_number)
            num_nodes = dir_info['num_nodes']
            num_nodes +=1

            dir_map.update_one(
                {'name': dir_name},
                {
                    '$set':{
                        'ports': port_list,
                        'num_nodes': num_nodes
                    }
                }
            )



class dir_ports_API(Resource):
    def get(self, directory):
        d = dir_map.find_one({'name': directory})
        ports = d['ports']
        response = {
            'dir_name': directory,
            'ports': ports
        }
        return jsonify(response)

    




api.add_resource(Directory_API, '/api/files/<string:file_name>', endpoint = 'file')
api.add_resource(Node_Init_API, '/api/node/<string:port_number>', endpoint = 'node')
api.add_resource(dir_ports_API, '/api/ports/<string:directory>')

if __name__ == '__main__':
    db.drop_collection('file_map')
    db.drop_collection('dir_map')
    db.drop_collection('active_nodes')

    server_port = int(sys.argv[1])

    server_init_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
    data = {
        'dir_port': server_port
    }
    requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)
    app.run(host= '0.0.0.0', port = server_port, debug = True)
