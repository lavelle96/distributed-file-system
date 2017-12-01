#!/bin/bash
source config.cfg
echo $server_port_2
python File_Server.py "$server_port_2" "$dir_server_port"
