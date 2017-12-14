from flask import Flask, request, jsonify, abort
from flask_restful import Api,Resource
import config as cf
from utils import get_file_read, update_file, delete_file, does_file_exist, clear_path
from datetime import datetime
import sys
import os
from pymongo import MongoClient
import requests
import json
from format import format_registry_req

client = MongoClient()
db = client.cache_db
file_timestamps = db.file_timestamps
'''
{
    'file_name':
    'timestamp':
}
'''

#TODO: Doesnt allow folder control (see cache folders)

app = Flask(__name__)
api = Api(app)

def cache_is_full():
    if file_timestamps.count() >= cf.CACHE_FILE_CAPACITY:
        return True
    return False

def get_LRU_file():
    '''returns file name of the least recently used
    file in the cache
    '''
    latest = datetime.now()
    latest_index = -1
    files = file_timestamps.find()
    for element in files:
        if element['timestamp'] < latest:
            latest = element['timestamp']
            file_name = element['file_name']
    return file_name

def clear_cache():
    clear_path(cf.CACHE_FILE_PATH)


class Cache_API(Resource):
    def get(self):
        '''Gets a request for a file, if it exists in the cache, it returns it'''
        data = request.json
        file_name = data['file_name']
        file_exist = does_file_exist(file_name, cf.CACHE_FILE_PATH)
        cache_miss = False
        if not file_exist:
            cache_miss = True
        else:
            file_timestamps.update_one(
                {'file_name': file_name},
                {
                    '$set':{
                        'name': file_name,
                        'timestamp': datetime.now()                    
                        }
                },
                upsert=True
            )
            
        response = {
                'cache_miss': cache_miss,
                'file_name': file_name,
        }
        print('cache_response: ', cache_miss)
        return jsonify(response)

    def post(self):
        '''Adds file to cache, performed on reads, also updates a file in the cache if it exists,
        performed on writes'''
        print('post received, cache size is: ', file_timestamps.count())
        
        if(not request.is_json):
            abort(400)
        data = request.json
        file_content = data['file_content']
        file_name = data['file_name']
        #check if the file exists on the cache
        #check if the cache is full, if so, boot the most recently used
        #Create a the file in the cache
        #Add it to the timestamp map 

        if file_timestamps.find_one({'file_name': file_name}) == None:
            if cache_is_full():
                LRU = get_LRU_file()
                file_timestamps.remove({'file_name': LRU})
                delete_file(LRU, cf.CACHE_FILE_PATH)


        try:
            update_file(file_name, cf.CACHE_FILE_PATH, file_content)
            file_timestamps.update_one(
                {'file_name': file_name},
                {
                    '$set':{
                        'file_name': file_name,
                        'timestamp': datetime.now()
                    }
                },
                upsert=True
            )
        except:
            abort(403)

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
api.add_resource(Cache_API, '/api/file', endpoint= 'file')

if __name__ == '__main__':
    clear_cache()
    db.drop_collection('file_timestamps')
    server_port = int(sys.argv[1])
    server_init_url = format_registry_req('cache_server', cf.REGISTRY_SERVER_PORT)
    data = {
        'dir_port': server_port
    }
    requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)
    app.run(host= '0.0.0.0', port = server_port, debug = True)

