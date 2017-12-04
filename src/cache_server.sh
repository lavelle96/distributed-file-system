#!/bin/bash
source config.cfg
echo $cache_server_port
python Cache_Service.py "$cache_server_port" 