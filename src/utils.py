import os

def get_file(file_name, path):
    """Return file given file name and path name"""
    file_list = os.listdir(path)
    
    if file_name in file_list:
        f = open(path + '/' + file_name)
        return f.read()
       
    return None
