from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import config as cf

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

def get_response(port, dir_name):
    response = {
        'dir_name': dir_name,
        'dir_port': port
    }
    return jsonify(response)

class registry_API(Resource):
    def get(self, dir_name):
        '''Get port of directory name given'''
        servers = directories.find({'dir_name': dir_name})
        if servers = None:
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
            directories.insert_one(new_dir)
            return jsonify({
                'result': 'success'
            })
        except:
            return jsonify({
                'result': 'fail'
            })

api.add_resource(registry_API, '/api/dirs/<string:dir_name>')

if __name__ == '__main__':
    server_port = cf.REGISTRY_SERVER_PORT
    app.run('0.0.0.0', server_port)