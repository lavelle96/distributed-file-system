from flask import Flask, request, jsonify
from flask_restful import Api, Resource, abort
import requests
from format import format_file_req, format_registry_req
import sys
import json
import uuid
from pymongo import MongoClient
import config as cf

client = MongoClient()
db = client.lock_db
file_locks = db.file_locks

'''{
    'file_name':
    'is_locked':
    'lock_holders': [queue of client ids]
}'''

app = Flask(__name__)
api = Api(app)

#TODO: clean up code for get lock, if possible

#Two dicts: 
#one for mapping the file name to whether or not it's locked
#Another for mapping the filename to a queue where the first uuid in the queue is the person who has it locked and 
#the following uuids are the next in line


#api
#***Users ids will be needed to unlock the lock on a file***
#Get to get lock (lock the lock)


def update(file_name, lock_holders, is_locked):
    file_locks.update_one(
                    {'file_name': file_name},
                    {
                        '$set':{
                            'lock_holders': lock_holders,
                            'is_locked': is_locked
                        }
                    }
                )
def get_response(id, lock_acquired):
    response = {
        'client_id': id,
        'lock_acquired': lock_acquired
    }
    return response

def post_response(id, release_successful):
    response = {
        'client_id': id,
        'release_successful': release_successful
    }
    return response


class read_lock_API(Resource):
    def get(self, file_name, id):
        '''
        get request sent when a user is looking to acquire a lock
        '''
        #LOGIC: 
        #1.If the file doesnt exist in the dicts, add it to the dicts, lock it and send the clients uuid back to him
        #2.Else if the file isnt locked, check if the queue is empty, if it is return lock, otherwise check if the user is at the top of the queue, if he is: lock the file and send back the users uuid
        #If the file is locked, check if the user exists in the queue, if he does, send back a not available message, 
        #Other wise, create a new uuid for him, add him to the queue and 
        print('id: ', id)
        print('file name: ', file_name)

        if id == '0':
            id = str(uuid.uuid4())

        lock_acquired = False
        response = {
            "client_id": id,
            "lock_acquired": lock_acquired
        }

        #1
        file_lock = file_locks.find_one({'file_name': file_name})
        if file_lock == None:
            new_file_lock = {
                'file_name': file_name,
                'is_locked': True,
                'lock_holders': [id]
            }
            file_locks.insert_one(new_file_lock)
            lock_acquired = True
            response = {
                "client_id": id,
                "lock_acquired": lock_acquired
            }
            print('exit point 1')
            return jsonify(response)
        else:
            is_locked = file_lock['is_locked']
            lock_holders = file_lock['lock_holders']

        #2
        if is_locked == False:
            if lock_holders == []:
                is_locked = True
                lock_holders = [id]
                lock_acquired = True
                response = {
                    "client_id": id,
                    "lock_acquired": lock_acquired
                }
                update(file_name, lock_holders, is_locked)
                print('exit point 2')
                return jsonify(response)

            else:
                if lock_holders[0] == id:
                    is_locked = True
                    lock_acquired = True
                    response = {
                        "client_id": id,
                        "lock_acquired": lock_acquired
                    }
                    update(file_name, lock_holders, is_locked)
                    print('exit point 3')
                    return jsonify(response)
                else:
                    if not id in lock_holders:
                        lock_holders.append(id)
                        update(file_name, lock_holders, is_locked)
                    print('exit point 3')
                    return jsonify(response)
        else:
            if lock_holders[0] == id:
                lock_acquired = True
                response = {
                    "client_id": id,
                    "lock_acquired": lock_acquired
                }
                print('exit point 4')
                return jsonify(response)
            if not id in lock_holders:
                lock_holders.append(id)
                update(file_name, lock_holders, is_locked)
            print('exit point 5')
            return jsonify(response)
                    
    def post(self, file_name, id):
        '''
        post request sent when a user is releasing a lock
        '''
        #LOGIC - if lock is in possesion of the specified id, i.e., if the client is in the first position in the queue:
        #       remove the client from the queue, making sure to move the queue one to the left, also set is_locked to False
        '''
        response = {
            'release_successful': True/False
        }
        '''
        file_lock = file_locks.find_one({'file_name': file_name})
        if file_lock == None:
            return post_response(id, False)
        lock_holders = file_lock['lock_holders']
        is_locked = file_lock['is_locked']
        if is_locked == False or lock_holders == [] or lock_holders[0] != id:
            return post_response(id, False)
        is_locked = False
        lock_holders.pop(0)
        update(file_name, lock_holders, is_locked)
        return post_response(id, True)



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
api.add_resource(read_lock_API, '/api/lock/<string:file_name>/<string:id>')

if __name__ == '__main__':
    db.drop_collection('file_locks')

    

    server_port = int(sys.argv[1])
    server_init_url = format_registry_req('lock_server', cf.REGISTRY_SERVER_PORT)
    data = {
        'dir_port': server_port
    }
    requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)
    app.run(host= '0.0.0.0', port = server_port, debug = True)