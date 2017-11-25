import requests
from format import format_file_req
import json
import config as cf
import os
import sys


def read_file(file_name):
    """
    Allows user to read file of a particular name
    Will involve sending a get request to the fileservers api
    """
    url = format_file_req(file_name, cf.DIR_SERVER_PORT)
    response =  json.loads(requests.get(url).content.decode())
    print(response)
    f = open('temp/'+file_name, 'w+')
    f.write(response["file_content"])
    #The following line is specific to linux machines
    os.system('xdg-open '+ 'temp/'+file_name)
    
    

def write_file(file_name, file):
    """Allows user to write to file of a particular name"""
    url = format_file_req(file_name, cf.DIR_SERVER_PORT)
    data = {
        "file_name": file_name,
        "file_content": file.read()
    }
    response = requests.post(url, data)


def open_file(filename):
    """
    Prepares a file of a given name for reading - maybe
    adds it to cache without returning it?
    """

def close_file(filename):
    """
    Unsure of functionality needed here
    """
