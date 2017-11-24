import Lib
import sys

server_port = sys.argv[1]
print(Lib.read("2.2", server_port))