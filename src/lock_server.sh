#!/bin/bash
source config.cfg
echo $lock_server_port
python Lock_Server.py "$lock_server_port" 