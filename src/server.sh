#!/bin/bash
source config.cfg
echo $server_port
python File_Server.py "$server_port" 