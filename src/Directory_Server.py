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
    'dir':
    'port':
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
    'supported': False
}
DIR_2 = {
    'name': 'D2',
    'supported': False
}
#Map of Directory to Node

class Directory_API(Resource):
    def get(self, file_name):
        
        f = file_map.find_one({'name': file_name})
        if f == None:
            abort(404)
        file_dir = f['dir']
        d = dir_map.find_one({'name': file_dir})
        if d['supported'] == False:
            abort(404)
        node = active_nodes.find_one({'dir': file_dir})
        response = {
            'file_server_port': node['port']
        }
        return jsonify(response)

class Node_Init_API(Resource):
    def get(self, port_number):
        query = dir_map.find()
        for i in query:
            print(i)

        node = active_nodes.find_one({'port': port_number})
        if node != None:
            response = {"file_dir": node['dir']}
            print('response to port ', str(port_number), ' ', response)
            return jsonify(response)


        d = dir_map.find_one({"supported": False})
        if d==None:
            return d
        dir_map.update_one(
            {"name": d['name']},
            {
                '$set':{
                    "supported": True
                }
            }
        )
        active_nodes.insert_one({
            'dir': d['name'],
            'port': port_number
        })

        response = {
            "file_dir": d['name']
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
