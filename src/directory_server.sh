#!/bin/bash
source config.cfg
echo $dir_server_port
python Directory_Server.py "$dir_server_port" 