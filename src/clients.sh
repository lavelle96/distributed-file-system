#!/bin/bash
source config.cfg
echo $server_port
python Client.py "$dir_server_port"
