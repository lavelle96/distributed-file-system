#!/bin/bash
source config.cfg
echo $auth_server_port
python Auth_Server.py "$auth_server_port" 