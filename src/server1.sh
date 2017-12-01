#!/bin/bash
source config.cfg
echo $server_port_1
python File_Server.py "$server_port_1" "$dir_server_port"
