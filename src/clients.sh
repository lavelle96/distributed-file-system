#!/bin/bash
source config.cfg
echo $server_port
python Client.py "$server_port"
