#!/bin/bash
source config.cfg
echo $lock_server_port
python lock_server.py "$lock_server_port" 