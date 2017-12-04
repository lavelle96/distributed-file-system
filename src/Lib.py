import requests
from format import format_file_req, format_lock_req, format_registry_req
from utils import get_file_read
import json
import config as cf
import os
import sys
import time

def check_port(port):
    if str(port) == str(-1):
        print('port returned -1')
        sys.exit()
    

def read_file(file_name):
    """
    Allows user to read file of a particular name
    Will involve sending a get request to the fileservers api
    """
    #Get server ports from registry
    
    cache_url = format_registry_req('cache_server', cf.REGISTRY_SERVER_PORT)
    response = json.loads(requests.get(cache_url).content.decode())
    cache_port = response['dir_port']
    check_port(cache_port)
    

    dir_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
    response = json.loads(requests.get(dir_url).content.decode())
    dir_port = response['dir_port']
    check_port(dir_port)

    #Check if cached
    url = format_file_req(file_name, cache_port)
    response = json.loads(requests.get(url).content.decode())
    print('cache response: ', response)
    if response['cache_miss'] == False:
        file_content = get_file_read(file_name, cf.CACHE_FILE_PATH)
    else:
        #No lock needed for reading

        #Get file server port
        url = format_file_req(file_name, dir_port)
        response =  json.loads(requests.get(url).content.decode())
        file_server_port = response['file_server_port']

        #Get file from file server
        url = format_file_req(file_name, file_server_port)
        response =  json.loads(requests.get(url).content.decode())
        file_content = response["file_content"]

        #post to the cache
        url = format_file_req(file_name, cache_port)
        data = {
            'file_content': file_content
        }
        response = requests.post(url, data=json.dumps(data), headers=cf.JSON_HEADER)
        

    f = open('temp/'+file_name, 'w')
    f.write(file_content)
    f.close()
    #The following line is specific to linux machines
    os.system('xdg-open '+ 'temp/'+file_name)
    return 
    
    

def write_file(file_name):
    """Allows user to write to file of a particular name"""
    #Get server ports from registry
    cache_url = format_registry_req('cache_server', cf.REGISTRY_SERVER_PORT)
    response = json.loads(requests.get(cache_url).content.decode())
    cache_port = response['dir_port']
    check_port(cache_port)

    dir_url = format_registry_req('dir_server', cf.REGISTRY_SERVER_PORT)
    response = json.loads(requests.get(dir_url).content.decode())
    dir_port = response['dir_port']
    check_port(dir_port)
    
    lock_url = format_registry_req('lock_server', cf.REGISTRY_SERVER_PORT)
    response = json.loads(requests.get(lock_url).content.decode())
    lock_port = response['dir_port']
    check_port(lock_port)


    #Get lock
    lock_url = format_lock_req(file_name, '0', lock_port)
    response = json.loads(requests.get(lock_url).content.decode())
    lock_acquired = response['lock_acquired']
    client_id = response['client_id']
    lock_url = format_lock_req(file_name, client_id, lock_port)
    while(not lock_acquired):
        time.sleep(1)
        response = json.loads(requests.get(lock_url).content.decode())
        lock_acquired = response['lock_acquired']

    #Read File in
    read_file(file_name)

    input('Press enter to write file back to server')

    #Get file server port from directory server
    url = format_file_req(file_name, dir_port)
    response =  json.loads(requests.get(url).content.decode())
    file_server_port = response['file_server_port']

    #post to file server
    url = format_file_req(file_name, file_server_port)
    f = open('temp/'+file_name, 'r')
    file_content = f.read()
    data = {
        "file_name": file_name,
        "file_content": file_content
    }
    headers = cf.JSON_HEADER
    response = requests.post(url, data = json.dumps(data), headers = headers)

    #release lock
    requests.post(lock_url)

    #update cache
    url = format_file_req(file_name, cache_port)
    response = requests.post(url, json.dumps(data), headers=headers)


def open_file(filename):
    """
    Prepares a file of a given name for reading - maybe
    adds it to cache without returning it?
    """

def close_file(filename):
    """
    Unsure of functionality needed here
    """
