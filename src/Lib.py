import requests
import config
from format import format_file_req
import json

def read(file_name, server_port):
    """
    Allows user to read file of a particular name
    Will involve sending a get request to the fileservers api
    """
    url = format_file_req(file_name, server_port)
    response =  json.loads(requests.get(url).content.decode())
    return response

def write(file_name, file):
    """Allows user to write to file of a particular name"""


def open(filename):
    """
    Prepares a file of a given name for reading - maybe
    adds it to cache without returning it?
    """

def close(filename):
    """
    Unsure of functionality needed here
    """
