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
    'file_name':
    'num_nodes:
    'ports':
    'file_version':
}   
'''

active_nodes = db.active_nodes
'''
{
    'port':
    'file_names': []
    'load':
    
}
'''
app = Flask(__name__)
api = Api(app)



class Directory_API(Resource):
    '''Api used to get the port of a specific file'''
    def get(self):
        data = request.json
        file_name = data['file_name']
        f = file_map.find_one({'file_name': file_name})
        if f == None or f['num_nodes'] == 0:
            abort(404)
        ports = f['ports']
        
        #Return least loaded port
        min_load = None
        port = 0
        for p in ports:
            node = active_nodes.find_one({'port': p})
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
        print('reponse: ', response)
        return jsonify(response)

    def post(self):
        '''
        Endpoint for creating and updating file
                'file_name': ,
                'file_content': ,
                'file_server_port': ,
                'new_file': 
        '''
        data = request.json
        file_name = data['file_name']
        file_server_port = data['file_server_port']
        new_file = data['new_file']
        file_content = data['file_content']

        #Create file
        if new_file:
            #Handle db synchroniation
            db_node = active_nodes.find_one({'port': file_server_port})
            if not db_node:
                print('Server isnt registered: ', file_server_port)
                return
            
            #Add file to map if it hasnt been created, add it as a supported file in a node if it hasnt before
            db_file = file_map.find_one({'file_name': file_name})
            if db_file != None:
                print('file ' , file_name, ' already exists, updating db')
                ports = db_file["ports"]
                if not file_server_port in ports:
                    ports.append(file_server_port)
                    file_map.update_one(
                        {'file_name': file_name},
                        {
                            '$inc':{
                                'num_nodes': 1
                            },
                            '$set':{
                                'ports': ports
                            }
                        }
                    )
            else:
                
                new_file = {
                    'file_name': file_name,
                    'ports': [file_server_port],
                    'num_nodes': 1,
                    'file_version': 1
                }
                print('inserting new file: ', file_name)
                file_map.insert_one(new_file)

            file_list = db_node['file_names']
            if not file_name in file_list:
                file_list.append(file_name)
                active_nodes.update_one(
                    {'port': file_server_port},
                    {
                        '$set':{
                            'file_names': file_list
                        }
                    }
                )  
        #Update file
        else:
            d = file_map.find_one({'file_name': file_name})
            #increment file version
            file_map.update_one(
                {'file_name': file_name},
                {
                    '$inc':{
                        'file_version': 1
                    }
                }
            )
            #Replicate update across other nodes
            ports = d['ports']
            data = {
                'file_name': file_name,
                'file_content': file_content,
                'replicate': False,
                'new_file': new_file
            }
            print('request to replicate received from ', file_server_port)
            for port in ports:
                if str(port) != str(file_server_port):
                    print('sending request to ', port)
                    req = format_file_req(port)
                    requests.post(req, data=json.dumps(data), headers = cf.JSON_HEADER)
                    print('request sent to, ', port)
            print('finished replication')
            return 
         
    def delete(self):
        """
        Used to delete a file from the database
        {
            'file_name':
            'file_server_port':
        }
        """
        data = request.json
        file_name = data['file_name']
        file_server_port = data['file_server_port']
        db_f = file_map.find_one({'file_name': file_name})
        ports = db_f['ports']
        data = {
            'file_name': file_name,
            'replicate': False
        }
        for p in ports:
            if str(p) != str(file_server_port):
                req = format_file_req(p)
                requests.delete(req, data=json.dumps(data), headers=cf.JSON_HEADER)
                db_s = active_nodes.find_one({'port': p})
                file_names = db_s['file_names']
                file_names.remove(file_name)
                file_map.update_one(
                    {'port': p},
                    {
                        '$set':{'file_names': file_names}
                    }
                )
        file_map.delete_one({'file_name': file_name})
            

        
        



class Node_State_API(Resource):

    def post(self, port_number):
        '''
        Allows file servers to post the name of their directory and all the files contained in it
        request data:
        data={
            file_names:[]
        }
        '''
        if(not request.is_json):
            abort(400)
        data = request.json
        print('new node up and running, data: ', data)
        file_names = data['file_names']
        new_node = {
            'port': port_number,
            'file_names': file_names,
            'load': 0
        }
        active_nodes.update_one({
            'port': port_number},
            {
                '$set':new_node
            },
            upsert=True
        )
        for f in file_names:
            db_file = file_map.find_one({'file_name': f})
            if db_file:
                ports = db_file["ports"]
                ports.append(port_number)
                file_map.update_one(
                    {'file_name': f},
                    {
                        '$inc':{
                            'num_nodes': 1
                        },
                        '$set':{
                            'ports': ports
                        }
                    }
                )
            else:
                new_file = {
                    'file_name': f,
                    'ports': [port_number],
                    'num_nodes': 1,
                    'file_version': 1
                }
                file_map.insert_one(new_file)
                
    def delete(self, port_number):
        '''Endpoint to alert dir server of file server gone down'''
        node = active_nodes.find_one({'port': port_number})
        if node == None:
            return
        #Take it off as supporting node from file map, then remove it as an active node
        files_supported = node['file_names']
        for f in files_supported:
            db_f = file_map.find_one({'file_name': f})
            if db_f:
                supporting_nodes = db_f['ports']
                supporting_nodes.remove(port_number)
                num_nodes = db_f['num_nodes']
                num_nodes -= 1
                file_map.update_one({'file_name': f},
                {
                    '$set':{
                        'ports': supporting_nodes,
                        'num_nodes': num_nodes
                    }
                })
        active_nodes.delete_one({'port': port_number})
        return 


class file_ports_API(Resource):
    '''Api that gives back the ports that a given file is stored on'''
    def get(self):
        data = request.json
        file_name = data['file_name']
        d = file_map.find_one({'file_name': file_name})
        ports = d['ports']
        response = {
            'file_name': file_name,
            'ports': ports
        }
        return jsonify(response)

    
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

class get_files_API(Resource):
    '''Api that gets all files that the directory server knows of'''
    def get(self):
        files = file_map.find()
        file_list = []
        for f in files:
            file_list.append(f['file_name'])
        response = {
            'file_list': file_list
        }
        return response


class update_API(Resource):
    '''API used to manage synchronisation of db'''
    def post(self):
        '''
        data = {
                'file_name': ,
                'file_content': ,
                'fs_port': ,
                'new_file': 
            }
        '''
        #upate 


api.add_resource(Directory_API, '/api/file', endpoint = 'file')
api.add_resource(Node_State_API, '/api/node/<string:port_number>', endpoint = 'node')
api.add_resource(file_ports_API, '/api/ports')
api.add_resource(get_files_API, '/api/files')
api.add_resource(state_API, '/api/state')
api.add_resource(update_API, '/api/update')


if __name__ == '__main__':
    db.drop_collection('file_map')
    db.drop_collection('active_nodes')

    server_port = int(sys.argv[1])

    server_init_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
    data = {
        'dir_port': server_port
    }
    requests.post(server_init_url, data=json.dumps(data), headers=cf.JSON_HEADER)
    app.run(host= '0.0.0.0', port = server_port, debug = True)
