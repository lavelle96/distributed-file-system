from flask import Flask
import config
import sys
import os

app = Flask(__name__)


@app.route('/')
def hw():
    return "Hello world"

if __name__ == '__main__':
    
    server_port = int(sys.argv[1])
    app.run(host= '0.0.0.0', port = server_port, debug = True)