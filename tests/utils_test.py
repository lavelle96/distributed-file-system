import sys
SRC_PATH = "/home/lavelld/Documents/SS/Internet_Apps/DFS/src"
sys.path.append(SRC_PATH)
from utils import get_file_read, update_file


if __name__ == '__main__':
    test = int(sys.argv[1])
    if test == 0:
        test_path = SRC_PATH+ '/' + 'D1'

        print(get_file_read("1.1", test_path))
    if test == 1:
        test_path = SRC_PATH + '/' + 'cache'
        file_name = '1.1'
        file_content = 'Hello test'
        print(update_file(file_name, test_path, file_content))