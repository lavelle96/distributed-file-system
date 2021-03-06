import requests
from format import format_file_req, format_lock_req, format_registry_req, format_show_files, format_admin_req, format_login_req, format_users_req
from utils import get_file_read, split_path, get_port, add_and_get_file, get_file_port
import json
import config as cf
import os
import sys
import time

def check_port(port):
    if port == None:
        print('port returned -1')
        sys.exit()
    

def read_file(file_name):
    """
    Allows user to read file of a particular name
    Will involve sending a get request to the fileservers api
    """
    file_name_data = {'file_name': file_name}
    

    #Get server ports from registry
    cache_port = get_port('cache_server')
    check_port(cache_port)
    

    dir_port = get_port('dir_server')
    check_port(dir_port)

    #Check if cached
    url = format_file_req(cache_port)
    response = json.loads(requests.get(url, data=json.dumps(file_name_data), headers=cf.JSON_HEADER).content.decode())
    if response['cache_miss'] == False:
        file_content = get_file_read(file_name, cf.CACHE_FILE_PATH)
    else:
        #No lock needed for reading

        #Get file server port
        url = format_file_req(dir_port)
        try:
            response =  json.loads(requests.get(url, data=json.dumps(file_name_data), headers=cf.JSON_HEADER).content.decode())
            file_server_port = response['file_server_port']

        except:
            print('file doesnt exist')
            return
        
        #Get file from file server
        url = format_file_req(file_server_port)
        response =  json.loads(requests.get(url, data=json.dumps(file_name_data), headers=cf.JSON_HEADER).content.decode())
        file_content = response["file_content"]
        file_version = response['file_version']
        #post to the cache
        url = format_file_req(cache_port)
        data = {
            'file_name': file_name,
            'file_content': file_content,
            'file_version': file_version
        }
        response = requests.post(url, data=json.dumps(data), headers=cf.JSON_HEADER)
        
    script_dir = os.path.dirname(__file__)
    abs_file_path = script_dir + '/temp'
    f = add_and_get_file(file_name, abs_file_path)
    f.write(file_content)
    f.close()
    #The following line is specific to linux machines
    os.system('xdg-open '+ 'temp/'+file_name)
    return 
    
    

def write_file(file_name):
    """Allows user to write to file of a particular name"""
    file_name_data = {'file_name': file_name}
    #Get server ports from registry
    cache_port = get_port('cache_server')
    check_port(cache_port)

    dir_port = get_port('dir_server')
    check_port(dir_port)
    
    lock_port = get_port('lock_server')
    check_port(lock_port)


    #Get lock
    lock_url = format_lock_req('0', lock_port)
    response = json.loads(requests.get(lock_url, data=json.dumps(file_name_data), headers=cf.JSON_HEADER).content.decode())
    
    lock_acquired = response['lock_acquired']
    client_id = response['client_id']
    lock_url = format_lock_req(client_id, lock_port)
    while(not lock_acquired):
        time.sleep(1)
        response = json.loads(requests.get(lock_url, data=json.dumps(file_name_data), headers=cf.JSON_HEADER).content.decode())
        lock_acquired = response['lock_acquired']

    #Read File in
    read_file(file_name)

    input('Press enter to write file back to server')

    #Get file server port from directory server
    url = format_file_req(dir_port)
    response =  json.loads(requests.get(url, data=json.dumps(file_name_data), headers=cf.JSON_HEADER).content.decode())
    file_server_port = response['file_server_port']

    #post to file server
    url = format_file_req(file_server_port)
    script_dir = os.path.dirname(__file__)
    abs_file_path = script_dir + '/temp'
    file_content = get_file_read(file_name, abs_file_path)
    
    data = {
        "file_name": file_name,
        "file_content": file_content,
        "replicate": True,
        "new_file": False
    }
    headers = cf.JSON_HEADER
    response = json.loads(requests.post(url, data = json.dumps(data), headers = headers).content.decode())
    file_version = response['file_version']

    #release lock
    requests.post(lock_url, data=json.dumps(file_name_data), headers=cf.JSON_HEADER)

    data = {
        'file_name': file_name,
        'file_content': file_content,
        'file_version': file_version
    }
    #update cache
    url = format_file_req(cache_port)
    response = requests.post(url, json.dumps(data), headers=headers)

def create_file(file_name):
    """
    Creates file
    """
    file_server = get_port('file_server')
    check_port(file_server)
    data = {
        "file_name": file_name,
        'file_content': " ",
        'replicate': True,
        'new_file': True
    }
    req = format_file_req(file_server)
    requests.post(req, data = json.dumps(data), headers=cf.JSON_HEADER)




def delete_file(file_name):
    """
    Deletes file
    """
    dir_server_port = get_port('dir_server')
    check_port(dir_server_port)
    try: 
        file_port = get_file_port(file_name, dir_server_port)
    except:
        print('File doesnt exist')
        return
    req = format_file_req(file_port)
    data = {
        'file_name': file_name,
        'replicate': True
    }
    try:
        requests.delete(req, data=json.dumps(data), headers=cf.JSON_HEADER)
    except:
        print('unable to delete file')
    


def show():
    '''
    Shows files available
    '''
    dir_port = get_port('dir_server')
    check_port(dir_port)

    show_url = format_show_files(dir_port)
    response = json.loads(requests.get(show_url).content.decode())
    file_list = response['file_list']
    print('available files:')
    for f in file_list:
        print(f)

def user_login(username, password):
    '''
    returns true if login is successful
    '''
    auth_port = get_port('auth_server')
    req = format_login_req(auth_port)
    data = {
        'username': username,
        'password': password
    }
    response = json.loads(requests.get(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
    return response['valid_user']

def admin_login(admin_username, admin_password):
    '''
    returns true if login is successful
    '''
    auth_port = get_port('auth_server')
    req = format_admin_req(auth_port)
    data = {
        'admin_username': admin_username,
        'admin_password': admin_password
    }
    response = json.loads(requests.get(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
    return response['valid_admin']

def add_user(admin_username, admin_password, new_username, new_password, new_privilege):
    '''
    adds user to db if admin cred are accurate
    '''
    auth_port = get_port('auth_server')
    req = format_admin_req(auth_port)
    data = {
        'admin_username': admin_username,
        'admin_password': admin_password,
        'new_username': new_username,
        'new_password': new_password,
        'new_privilege': new_privilege
    }
    response = json.loads(requests.post(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
    return response['success']

def show_users(admin_username, admin_password):
    '''
    prints existing users if admin credentials are accurate
    '''
    auth_port = get_port('auth_server')
    req = format_users_req(auth_port)
    data = {
        'admin_username': admin_username,
        'admin_password': admin_password
    }
    response = json.loads(requests.get(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
    user_list = response['user_list']
    print('Users:')
    for u in user_list:
        print(u)

