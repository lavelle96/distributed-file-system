from flask import Flask, request, jsonify, request, abort
from flask_restful import Api,Resource
import config as cf
from utils import get_file_read, update_file, delete_file
from datetime import datetime
import sys
import os

app = Flask(__name__)
api = Api(app)

#Dictionary of file_names to timestamps
FILE_TIMESTAMP = {}

def cache_is_full():
    if len(FILE_TIMESTAMP) >= cf.CACHE_FILE_CAPACITY:
        return True
    return False

def get_LRU_file():
    latest = datetime.now()
    latest_index = -1
    for f in FILE_TIMESTAMP.keys():
        if FILE_TIMESTAMP[f] < latest:
            latest = FILE_TIMESTAMP[f]
            latest_index = f
    return latest_index

def clear_cache():
    file_list = os.listdir(cf.CACHE_FILE_PATH)
    for f in file_list:
        os.remove(cf.CACHE_FILE_PATH + '/' + f)


class Cache_API(Resource):
    def get(self, file_name):
        '''Gets a request for a file, if it exists in the cache, it returns it'''
        content = get_file_read(file_name, cf.CACHE_FILE_PATH)
        cache_miss = False
        if content == None:
            cache_miss = True
        else:
            FILE_TIMESTAMP[file_name] = datetime.now()
            
        response = {
                'cache_miss': cache_miss,
                'file_name': file_name,
                'file_content': content
            }
        return jsonify(response)

    def post(self, file_name):
        '''Adds file to cache, performed on reads, also updates a file in the cache if it exists,
        performed on writes'''
        print('post received, cache size is: ', len(FILE_TIMESTAMP))
        if(not request.is_json):
            abort(400)
        data = request.json
        file_content = data['file_content']
        #check if the file exists on the cache
        #check if the cache is full, if so, boot the most recently used
        #Create a the file in the cache
        #Add it to the timestamp map 
        if not (file_name in FILE_TIMESTAMP.keys()):
             if cache_is_full():
                LRU = get_LRU_file()
                print('LRU file is: ', LRU, '; about to delete it')
                del FILE_TIMESTAMP[LRU]
                delete_file(LRU, cf.CACHE_FILE_PATH)

        try:
            update_file(file_name, cf.CACHE_FILE_PATH, file_content)
            FILE_TIMESTAMP[file_name] = datetime.now()
        except:
            abort(403)

                


    
api.add_resource(Cache_API, '/api/files/<string:file_name>', endpoint= 'file')

if __name__ == '__main__':
    clear_cache()
    server_port = int(sys.argv[1])
    app.run(host= '0.0.0.0', port = server_port, debug = True)

