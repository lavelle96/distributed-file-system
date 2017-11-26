import os

def get_file_read(file_name, path):
    """Return contents of file with read privileges given file name and path name"""
    file_list = os.listdir(path)
    
    if file_name in file_list:
        f = open(path + '/' + file_name)
        return f.read()
       
    return None

def get_file_write(file_name, path):
    """Return file with write privileges given file name and path name"""
    file_list = os.listdir(path)
    
    if file_name in file_list:
        f = open(path + '/' + file_name, 'w')
        return f
       
def update_file(file_name, path, file_content):
    try:
        f = open(path + '/' + file_name, 'w')
        f.write(file_content)
        f.close()
        return True
    except:
        return None

def delete_file(file_name, path):
    try:
        os.remove(path + '/' + file_name)
        print('file deleted')
        return True
    except:
        return False