from flask import Flask, request, jsonify
from flask_restful import Api, Resource, abort
import requests
import json
import config as cf
from pymongo import MongoClient
import sys
from format import format_registry_req

app = Flask(__name__)
api = Api(app)
client = MongoClient()
db = client.auth_db
users = db.users
'''
{
username:
password:
privilege:
}
'''
def valid_admin(username, password):
    '''Returns true if they are a valid admin'''
    user = users.find_one(
            {
                'username': username,
                'password': password,
                'privilege': 'admin'
            }
        )
    response = False
    if user:
        response = True
    return response

def valid_user(username, password):
    '''Returns true if the user exists'''
    user = users.find_one(
            {
                'username': username,
                'password': password
                
            }
        )
    response = False
    if user:
        response = True
    return response

class auth_API(Resource):
    def get(self):
        '''
        returns true if its a valid user
        {
            username:
            password:
        }
        '''
        data = request.json
        username = data['username']
        password = data['password']
        valid = valid_user(username, password)
        response = {
            'valid_user': valid
        }
        return jsonify(response)

class admin_API(Resource):
    def get(self):
        '''
        returns true if the user is an admin
        {
            admin_username:
            admin_password:
        }
        '''
        data = request.json
        username = data['admin_username']
        password = data['admin_password']
        
        valid = valid_admin(username, password)
        response = {
            'valid_admin': valid
        }
        return jsonify(response)

    def post(self):
        '''
        Adds new user to the db
        {
            admin_username:
            admin_password:
            new_username:
            new_password:
            new_privilege:
        }
        '''
        data = request.json
        admin_username = data['admin_username']
        admin_password = data['admin_password']
        if not valid_admin(admin_username, admin_password):
            return jsonify({'success': False})

        new_username = data['new_username']
        new_password = data['new_password']
        new_privilege = data['new_privilege']
        new_user = {
            'username': new_username,
            'password': new_password,
            'privilege': new_privilege
        }
        users.update_one(new_user, {'$set':new_user}, upsert=True)
        return jsonify({'success': True})

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

class users_API(Resource):
    def get(self):
        '''returns list of users in db
        {
            admin_username:
            admin_password:
        }
        '''
        data = request.json
        admin_username = data['admin_username']
        admin_password = data['admin_password']
        if valid_admin(admin_username, admin_password) == False:
            return jsonify({'user_list': None})
        user_list = []
        db_users = users.find()
        for u in db_users:
            user_list.append(u['username'])
        
        return jsonify({'user_list': user_list})


api.add_resource(state_API, '/api/state')
api.add_resource(auth_API, '/api/login')
api.add_resource(admin_API, '/api/admin')
api.add_resource(users_API, '/api/users')

if __name__ == '__main__':
    admin = cf.ADMIN_DETAILS
    users.update_one(admin, {'$set': admin}, upsert=True)
    server_port = sys.argv[1]
    server_init_url = format_registry_req('auth_server', cf.REGISTRY_SERVER_PORT)
    data = {
        'dir_port': server_port
    }
    requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)
    app.run('0.0.0.0', int(server_port))
        
