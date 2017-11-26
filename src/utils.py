import os

def get_file_read(file_name, path):
    """Return file given file name and path name"""
    file_list = os.listdir(path)
    
    if file_name in file_list:
        f = open(path + '/' + file_name)
        return f.read()
       
    return None

def get_file_write(file_name, path):
    """Return file given file name and path name"""
    file_list = os.listdir(path)
    
    if file_name in file_list:
        f = open(path + '/' + file_name, 'w')
        return f
       
    return None