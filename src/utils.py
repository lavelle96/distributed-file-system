import os

def get_file(file_name, path):
    """Return file given file name and path name"""
    file_list = os.listdir(path)
    print(file_list)

    for root, dirs, files in os.walk(path):
        if file_name in files:
            f = open(path + '/' + file_name)
            return f.read()
    return None
