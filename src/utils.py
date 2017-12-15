import os
import requests
import json
import errno
import config as cf
import shutil
from format import format_registry_req, format_file_req

def get_file_read(file_name, path):
    """Return contents of file with read privileges given file name and path name"""
    file_list = os.listdir(path)
    for dir_, _, files in os.walk(path):
        for f in files:
            relDir = os.path.relpath(dir_, path)
            relFile = os.path.join(relDir, f)
            if relFile == file_name:
                file_match = open(path + '/' + file_name)
                return file_match.read()
       
    return None

def get_file_write(file_name, path):
    """Return file with write privileges given file name and path name"""
    file_list = os.listdir(path)
    for dir_, _, files in os.walk(path):
        for f in files:
            relDir = os.path.relpath(dir_, path)
            relFile = os.path.join(relDir, f)
            if relFile == file_name:
                file_match = open(path + '/' + file_name, 'w')
                return file_match
       
    return None

       
def update_file(file_name, path, file_content):
    '''updates file, adds it if it doesnt exist''' 
    if not os.path.exists(os.path.dirname(path+'/'+file_name)):
        try:
            os.makedirs(os.path.dirname(path+'/'+file_name))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(path + '/' + file_name, "w") as f:
        f.write(file_content)
        return True
    return None

def add_and_get_file(file_name, path):
    if not os.path.exists(os.path.dirname(path+'/'+file_name)):
        try:
            os.makedirs(os.path.dirname(path+'/'+file_name))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    try:
        f = open(path + '/' + file_name, "w") 
        return f
    except:
        return None

def delete_file(file_name, path):
    '''Deletes file at path'''
    try:
        os.remove(path + '/' + file_name)
        return True
    except:
        return False

def does_file_exist(file_name, path):
    '''returns true if file exists at given path'''
    file_list = os.listdir(path)
    for dir_, _, files in os.walk(path):
        for f in files:
            relDir = os.path.relpath(dir_, path)
            relFile = os.path.join(relDir, f)
            if relFile == file_name:
                return True
    return False
    
def get_files_in_dir(directory):
    '''gets files in directory'''
    rootDir = directory
    fileList = []

    for dir_, _, files in os.walk(rootDir):
        for fileName in files:
            relDir = os.path.relpath(dir_, rootDir)
            relFile = os.path.join(relDir, fileName)
            fileList.append(relFile)
    
    return fileList

def split_path(path):
     f = path.split("/", 1)[1]
     d = path.split('/', 1)[0]
     return d, f

def get_port(server_name):
    '''Gets port of given server from registry server, returns none if that server doesnt exist'''
    url = format_registry_req(server_name, cf.REGISTRY_SERVER_PORT)
    response = json.loads(requests.get(url).content.decode())
    port = response['dir_port']
    if str(port) == str(-1):
        print('port returned -1')
        return None
    return port

def clear_path(path):
    if path == '/' or path == '':
        return 
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def get_file_port(file_name, dir_server_port):
    req = format_file_req(dir_server_port)
    data = {
        'file_name': file_name
    }
    resp = json.loads(requests.get(req, data=json.dumps(data), headers=cf.JSON_HEADER).content.decode())
    port = resp['file_server_port']
    return port
