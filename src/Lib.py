import requests
from format import format_file_req, format_lock_req
from utils import get_file_read
import json
import config as cf
import os
import sys
import time


def read_file(file_name):
    """
    Allows user to read file of a particular name
    Will involve sending a get request to the fileservers api
    """
    #Check if cached
    url = format_file_req(file_name, cf.CACHE_SERVER_PORT)
    response = json.loads(requests.get(url).content.decode())
    print('cache response: ', response)
    if response['cache_miss'] == False:
        file_content = get_file_read(file_name, cf.CACHE_FILE_PATH)
    else:
        #No lock needed for reading

        #Get file server port
        url = format_file_req(file_name, cf.DIR_SERVER_PORT)
        response =  json.loads(requests.get(url).content.decode())
        file_server_port = response['file_server_port']

        #Get file from file server
        url = format_file_req(file_name, file_server_port)
        response =  json.loads(requests.get(url).content.decode())
        file_content = response["file_content"]

        #post to the cache
        url = format_file_req(file_name, cf.CACHE_SERVER_PORT)
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
    #Get lock
    lock_url = format_lock_req(file_name, '0', cf.LOCK_SERVER_PORT)
    response = json.loads(requests.get(lock_url).content.decode())
    lock_acquired = response['lock_acquired']
    client_id = response['client_id']
    lock_url = format_lock_req(file_name, client_id, cf.LOCK_SERVER_PORT)
    while(not lock_acquired):
        time.sleep(1)
        response = json.loads(requests.get(lock_url).content.decode())
        lock_acquired = response['lock_acquired']

    read_file(file_name)

    input('Press enter to write file back to server')

    #Get file server port from directory server
    url = format_file_req(file_name, cf.DIR_SERVER_PORT)
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
    url = format_file_req(file_name, cf.CACHE_SERVER_PORT)
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
