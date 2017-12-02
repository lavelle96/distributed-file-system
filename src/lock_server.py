from flask import Flask, request, jsonify
from flask_restful import Api, Resource, abort
import requests
from format import format_file_req
import sys
import json
import uuid

app = Flask(__name__)
api = Api(app)

#Two dicts: 
#one for mapping the file name to whether or not it's locked
#Another for mapping the filename to a queue where the first uuid in the queue is the person who has it locked and 
#the following uuids are the next in line
FILE_LOCKS = {}
LOCK_HOLDERS = {}

#api
#***Users ids will be needed to unlock the lock on a file***
#Get to get lock (lock the lock)
#1.If the file doesnt exist in the dicts, add it to the dicts, lock it and send the clients uuid back to him
#2.Else if the file isnt locked, check if the queue is empty, if it is return lock, otherwise check if the user is at the top of the queue, if he is: lock the file and send back the users uuid
#If the file is locked, check if the user exists in the queue, if he does, send back a not available message, 
#Other wise, create a new uuid for him, add him to the queue and 

class read_lock_API(Resource):
    def get(self, file_name, id):
        print('id: ', id)
        print('file name: ', file_name)
        if file_name in LOCK_HOLDERS:
            print('file user list: ', LOCK_HOLDERS[file_name])
            print('Is file locked: ', FILE_LOCKS[file_name])
        if id == '0':
            id = str(uuid.uuid4())
        

        if not file_name in FILE_LOCKS:
            print('file didnt exist before')
            FILE_LOCKS[file_name] = True
            
            LOCK_HOLDERS[file_name] = [id]
            response = {
                "client_id": id,
                "lock_acquired": True
            }
            return jsonify(response)

        if FILE_LOCKS[file_name] == False:
            if LOCK_HOLDERS[file_name] == []:
                FILE_LOCKS[file_name] = True
                LOCK_HOLDERS[file_name] = [id]
                response = {
                    "client_id": id,
                    "lock_acquired": True
                }
                return jsonify(response)
            else:
                if LOCK_HOLDERS[file_name][0] == id:
                    FILE_LOCKS[file_name] = True
                    response = {
                        "client_id": id,
                        "lock_acquired": True
                    }
                    return jsonify(response)
                else:
                    if not id in LOCK_HOLDERS[file_name]:
                        LOCK_HOLDERS[file_name].append(id)
                    response = {
                        "client_id": id,
                        "lock_acquired": False
                    }
                    return jsonify(response)
        else:
            if LOCK_HOLDERS[file_name][0] == id:
                response = {
                    "client_id": id,
                    "lock_acquired": True
                }
                return jsonify(response)
            if not id in LOCK_HOLDERS[file_name]:
                LOCK_HOLDERS[file_name].append(id)
            response = {
                "client_id": id,
                "lock_acquired": False
            }
            return jsonify(response)
            
        



        

#Post to post lock

#Might have a second api seperate from the reads

api.add_resource(read_lock_API, '/api/lock/<string:file_name>/<string:id>')

if __name__ == '__main__':
    server_port = int(sys.argv[1])
    app.run(host= '0.0.0.0', port = server_port, debug = True)