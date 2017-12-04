from flask import Flask, request, jsonify, request, abort
from flask_restful import Api,Resource
import config as cf
from utils import get_file_read, update_file, delete_file, does_file_exist
from datetime import datetime
import sys
import os
from pymongo import MongoClient
client = MongoClient()
db = client.cache_db
file_timestamps = db.file_timestamps
'''
{
    'name':
    'timestamp':
}
'''

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
            file_name = element['name']
    return file_name

def clear_cache():
    file_list = os.listdir(cf.CACHE_FILE_PATH)
    for f in file_list:
        os.remove(cf.CACHE_FILE_PATH + '/' + f)


class Cache_API(Resource):
    def get(self, file_name):
        '''Gets a request for a file, if it exists in the cache, it returns it'''
        file_exist = does_file_exist(file_name, cf.CACHE_FILE_PATH)
        cache_miss = False
        if not file_exist:
            cache_miss = True
        else:
            file_timestamps.update_one(
                {'name': file_name},
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
        return jsonify(response)

    def post(self, file_name):
        '''Adds file to cache, performed on reads, also updates a file in the cache if it exists,
        performed on writes'''
        print('post received, cache size is: ', file_timestamps.count())
        if(not request.is_json):
            abort(400)
        data = request.json
        file_content = data['file_content']
        #check if the file exists on the cache
        #check if the cache is full, if so, boot the most recently used
        #Create a the file in the cache
        #Add it to the timestamp map 

        if file_timestamps.find_one({'name': file_name}) == None:
            if cache_is_full():
                LRU = get_LRU_file()
                file_timestamps.remove({'name': LRU})
                delete_file(LRU, cf.CACHE_FILE_PATH)


        try:
            update_file(file_name, cf.CACHE_FILE_PATH, file_content)
            file_timestamps.update_one(
                {'name': file_name},
                {
                    '$set':{
                        'name': file_name,
                        'timestamp': datetime.now()
                    }
                },
                upsert=True
            )
        except:
            abort(403)

                


    
api.add_resource(Cache_API, '/api/files/<string:file_name>', endpoint= 'file')

if __name__ == '__main__':
    clear_cache()
    db.drop_collection('file_timestamps')
    server_port = int(sys.argv[1])
    app.run(host= '0.0.0.0', port = server_port, debug = True)

