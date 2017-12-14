import sys
SRC_PATH = "/home/lavelld/Documents/SS/Internet_Apps/DFS/src"
sys.path.append(SRC_PATH)
from utils import get_file_read, update_file, get_files_in_dir, split_path, clear_path, add_and_get_file


if __name__ == '__main__':
    test = int(sys.argv[1])
    if test == 0:
        test_path = SRC_PATH + '/FS_3'
        print(get_file_read("D1/1.1", test_path))

    if test == 1:
        test_path = SRC_PATH + '/' + 'cache'
        file_name = 'D1/1.1'
        file_content = 'Hello test'
        print(update_file(file_name, test_path, file_content))

    if test == 2:
        test_path = SRC_PATH + '/' + 'FS_1/D1'
        print(get_files_in_dir(test_path))
    elif test == 3:
        path = 'D1/1.1'
        print(split_path(path)[1])
    
    elif test == 4:
        test_path = SRC_PATH + '/' + 'temp'
        print(clear_path(test_path))

    elif test == 5:
        test_path = SRC_PATH + '/' + 'temp'
        file_name = 'D1/1.1'
        f = add_and_get_file(file_name, test_path)
        print(f.read())

