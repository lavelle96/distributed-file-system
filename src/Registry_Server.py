from flask import Flask, jsonify, request
from flask_restful import Api, Resource, abort
from pymongo import MongoClient
import config as cf
import requests
from threading import Thread
from format import format_state_request, format_node_req
import time

app = Flask(__name__)
api = Api(app)

client = MongoClient()
db = client.reg_db
directories = db.directories
'''
{
    dir_name:
    dir_port:
    dir_load: (used to decide which file server will handle the request)
}
'''
CHECK_FREQUENCY = 8 #seconds

def thread_node_check():
    while(1):
        servers = directories.find()
        for s in servers:
            port = s['dir_port']
            req = format_state_request(port)
            try:
                requests.get(req)
            except:
                #If its a file server, alert the directory server
                if str(s['dir_name']) == 'file_server':
                    dir_server = directories.find_one({'dir_name': 'dir_server'})
                    if dir_server:
                        dir_port = dir_server['dir_port']
                        req = format_node_req(port, dir_port)
                        requests.delete(req)
                #delete server from directory
                directories.delete_one({'dir_port': port})

        time.sleep(CHECK_FREQUENCY)

def get_response(port, dir_name):
    response = {
        'dir_port': port,
        'dir_name': dir_name
    }
    return jsonify(response)

class registry_API(Resource):
    def get(self, dir_name):
        '''Get port of directory name given'''
        servers = directories.find({'dir_name': dir_name})
        
        if servers == None or servers.count() < 1:
            return get_response(-1, dir_name)
        min_load = None
        server_to_return = None
        for server in servers:
            if min_load == None:
                min_load = server['dir_load']
                server_to_return = server
            else:
                if server['dir_load'] < min_load:
                    min_load = server['dir_load']
                    server_to_return = server
        
        dir_port = server_to_return['dir_port']
        directories.update(
            {'dir_name': dir_name, 'dir_port': dir_port},
            {
                '$inc':{
                    'dir_load': 1
                }
            }
        )
        response = get_response(dir_port, dir_name)
        return response

        
    def post(self, dir_name):
        '''post port for directory name given'''
        '''request form: {'dir_port':}'''
        if(not request.is_json):
            abort(400)
        data = request.json
        dir_port = data['dir_port']
        new_dir = {
            'dir_name': dir_name,
            'dir_port': dir_port,
            'dir_load': 0
        }
        try:
            directories.update_one(
                {'dir_name': dir_name, 'dir_port': dir_port},
                {
                    '$set':new_dir
                },
                upsert=True
            )
            return jsonify({
                'result': 'success'
            })
        except:
            return jsonify({
                'result': 'fail'
            })

api.add_resource(registry_API, '/api/dirs/<string:dir_name>')

if __name__ == '__main__':
    db.drop_collection('directories')
    node_check_thread = Thread(target=thread_node_check)
    node_check_thread.start()

    server_port = cf.REGISTRY_SERVER_PORT
    app.run('0.0.0.0', server_port)