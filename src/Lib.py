import requests
import config

def read(filename, server_port):
    """
    Allows user to read file of a particular name
    Will involve sending a get request to the fileservers api
    """
    url = 'http://localhost:' + server_port
    print(requests.get(url).content)

def write(filename, file):
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
